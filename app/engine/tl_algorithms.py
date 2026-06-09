"""
Traffic Light Algorithms

Custom TL control algorithms that override SUMO's built-in logic via TraCI.
Each algorithm is a callable that receives (traci_client, tl_id, sim_time).
"""

from __future__ import annotations
from typing import Optional
from app.models.traffic_light import TrafficLight, TLPhase, TLAlgorithm
from app.utils.logger import get_logger

logger = get_logger("tl_algo")


def fixed_time_controller(tl: TrafficLight, traci, sim_time: float):
    if not tl.phases:
        return

    elapsed = tl.get_elapsed(sim_time)
    current = tl.current_phase

    if current and elapsed >= current.duration:
        next_idx = current.next if current.next >= 0 else (current.index + 1) % len(tl.phases)
        tl.current_phase_index = next_idx
        tl.phase_start_time = sim_time
        try:
            next_phase = tl.phases[next_idx]
            traci.trafficlight.setPhase(tl.id, next_phase.index)
            traci.trafficlight.setPhaseDuration(tl.id, next_phase.duration)
        except Exception as e:
            logger.warning(f"setPhase failed for {tl.id}: {e}")


def actuated_controller(tl: TrafficLight, traci, sim_time: float):
    if not tl.phases:
        return

    elapsed = tl.get_elapsed(sim_time)
    current = tl.current_phase
    if not current:
        return

    if elapsed < tl.min_green:
        return

    import traci as tc
    try:
        detector_ids = tc.inductionloop.getIDList()
        vehicle_detected = any(
            tc.inductionloop.getLastStepVehicleNumber(d) > 0
            for d in detector_ids
        )
    except Exception:
        vehicle_detected = False

    if vehicle_detected:
        tl.gap_timer = 0.0
        if elapsed + tl.extension <= tl.max_green:
            try:
                tc.trafficlight.setPhaseDuration(
                    tl.id, tl.max_green - elapsed + tl.extension
                )
            except Exception:
                pass
        else:
            _switch_to_next(tl, traci, sim_time)
    else:
        tl.gap_timer += 1.0
        if tl.gap_timer >= tl.gap_out:
            _switch_to_next(tl, traci, sim_time)

    if elapsed >= tl.max_green:
        _switch_to_next(tl, traci, sim_time)


def max_pressure_controller(tl: TrafficLight, traci, sim_time: float):
    """Varaiya 2013 - pick phase with highest queue pressure."""
    if sim_time - tl.last_pressure_calc < tl.pressure_interval:
        return
    tl.last_pressure_calc = sim_time

    import traci as tc
    try:
        edge_ids = tc.edge.getIDList()
        pressures = {}
        for edge_id in edge_ids[:50]:
            vehicle_count = tc.edge.getLastStepVehicleNumber(edge_id)
            speed = tc.edge.getLastStepMeanSpeed(edge_id)
            pressure = vehicle_count * max(0.5, 1.0 - speed / 13.89)
            pressures[edge_id] = pressure

        best_idx = 0
        best_pressure = -float("inf")
        for i, phase in enumerate(tl.phases):
            p = pressures.get(f"edge_{i}", 0.0)
            if p > best_pressure:
                best_pressure = p
                best_idx = i

        if best_pressure > 0:
            tl.current_phase_index = best_idx
            tl.phase_start_time = sim_time
            tc.trafficlight.setPhase(tl.id, best_idx)
            tc.trafficlight.setPhaseDuration(tl.id, 10.0)
    except Exception as e:
        logger.warning(f"max_pressure error: {e}")


def green_wave_controller(tl: TrafficLight, traci, sim_time: float):
    """Coordinated TL with offset based on distance / target speed."""
    adjusted_time = (sim_time + tl.offset) % tl.cycle_time
    for i, phase in enumerate(tl.phases):
        phase_start = sum(tl.phases[j].duration for j in range(i))
        phase_end = phase_start + phase.duration
        if phase_start <= (adjusted_time % tl.cycle_time) < phase_end:
            if i != tl.current_phase_index:
                tl.current_phase_index = i
                tl.phase_start_time = sim_time
                try:
                    traci.trafficlight.setPhase(tl.id, i)
                    traci.trafficlight.setPhaseDuration(tl.id, phase.duration)
                except Exception as e:
                    logger.warning(f"green_wave setPhase error: {e}")
            break


def _switch_to_next(tl: TrafficLight, traci, sim_time: float):
    if not tl.phases:
        return
    next_idx = (tl.current_phase_index + 1) % len(tl.phases)
    tl.current_phase_index = next_idx
    tl.phase_start_time = sim_time
    tl.gap_timer = 0.0
    try:
        next_phase = tl.phases[next_idx]
        traci.trafficlight.setPhase(tl.id, next_phase.index)
        traci.trafficlight.setPhaseDuration(tl.id, next_phase.duration)
    except Exception as e:
        logger.warning(f"_switch_to_next error: {e}")


ALGORITHM_MAP = {
    "fixed": fixed_time_controller,
    "actuated": actuated_controller,
    "max_pressure": max_pressure_controller,
    "green_wave": green_wave_controller,
}


def get_controller(algorithm: str):
    return ALGORITHM_MAP.get(algorithm, fixed_time_controller)

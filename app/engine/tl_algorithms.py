from __future__ import annotations

from typing import Callable, Optional

from app.models.traffic_light import TrafficLight, TLPhase, TLAlgorithm
from app.utils.logger import get_logger

logger = get_logger("tl_algo")


def fixed_time_controller(
    tl: TrafficLight,
    traci_module,
    sim_time: float,
    step_length: float = 1.0,
) -> None:
    if not tl.phases:
        return

    elapsed = tl.get_elapsed(sim_time)
    current = tl.current_phase

    if current and elapsed >= current.duration:
        next_idx = (
            current.next if current.next >= 0
            else (current.index + 1) % len(tl.phases)
        )
        tl.current_phase_index = next_idx
        tl.phase_start_time = sim_time
        try:
            next_phase = tl.phases[next_idx]
            traci_module.trafficlight.setPhase(tl.id, next_phase.index)
            traci_module.trafficlight.setPhaseDuration(tl.id, next_phase.duration)
        except Exception as e:
            logger.warning(f"setPhase failed for {tl.id}: {e}")


def actuated_controller(
    tl: TrafficLight,
    traci_module,
    sim_time: float,
    step_length: float = 1.0,
) -> None:
    if not tl.phases:
        return

    elapsed = tl.get_elapsed(sim_time)
    current = tl.current_phase
    if not current:
        return

    if elapsed < tl.min_green:
        return

    try:
        detector_ids = traci_module.inductionloop.getIDList()
        vehicle_detected = any(
            traci_module.inductionloop.getLastStepVehicleNumber(d) > 0
            for d in detector_ids
        )
    except Exception:
        vehicle_detected = False

    if vehicle_detected:
        tl.gap_timer = 0.0
        if elapsed + tl.extension <= tl.max_green:
            try:
                traci_module.trafficlight.setPhaseDuration(
                    tl.id, tl.max_green - elapsed + tl.extension
                )
            except Exception:
                pass
        else:
            _switch_to_next(tl, traci_module, sim_time)
    else:
        tl.gap_timer += step_length
        if tl.gap_timer >= tl.gap_out:
            _switch_to_next(tl, traci_module, sim_time)

    if elapsed >= tl.max_green:
        _switch_to_next(tl, traci_module, sim_time)


def max_pressure_controller(
    tl: TrafficLight,
    traci_module,
    sim_time: float,
    step_length: float = 1.0,
) -> None:
    """Simplified: pick phase with highest incoming vehicle count."""
    if sim_time - tl.last_pressure_calc < tl.pressure_interval:
        return
    tl.last_pressure_calc = sim_time

    try:
        edge_ids = traci_module.edge.getIDList()[:50]
        best_idx = 0
        best_pressure = -1.0

        for i, phase in enumerate(tl.phases):
            pressure = 0.0
            for eid in edge_ids:
                count = traci_module.edge.getLastStepVehicleNumber(eid)
                speed = traci_module.edge.getLastStepMeanSpeed(eid)
                pressure += count * max(0.5, 1.0 - speed / 13.89)
            if pressure > best_pressure:
                best_pressure = pressure
                best_idx = i

        if best_pressure > 0:
            tl.current_phase_index = best_idx
            tl.phase_start_time = sim_time
            traci_module.trafficlight.setPhase(tl.id, best_idx)
            traci_module.trafficlight.setPhaseDuration(tl.id, 10.0)
    except Exception as e:
        logger.warning(f"max_pressure error: {e}")


def green_wave_controller(
    tl: TrafficLight,
    traci_module,
    sim_time: float,
    step_length: float = 1.0,
) -> None:
    adjusted_time = (sim_time + tl.offset) % tl.cycle_time
    for i, phase in enumerate(tl.phases):
        phase_start = sum(tl.phases[j].duration for j in range(i))
        phase_end = phase_start + phase.duration
        if phase_start <= (adjusted_time % tl.cycle_time) < phase_end:
            if i != tl.current_phase_index:
                tl.current_phase_index = i
                tl.phase_start_time = sim_time
                try:
                    traci_module.trafficlight.setPhase(tl.id, i)
                    traci_module.trafficlight.setPhaseDuration(
                        tl.id, phase.duration
                    )
                except Exception as e:
                    logger.warning(f"green_wave setPhase error: {e}")
            break


def _switch_to_next(
    tl: TrafficLight,
    traci_module,
    sim_time: float,
) -> None:
    if not tl.phases:
        return
    next_idx = (tl.current_phase_index + 1) % len(tl.phases)
    tl.current_phase_index = next_idx
    tl.phase_start_time = sim_time
    tl.gap_timer = 0.0
    try:
        next_phase = tl.phases[next_idx]
        traci_module.trafficlight.setPhase(tl.id, next_phase.index)
        traci_module.trafficlight.setPhaseDuration(tl.id, next_phase.duration)
    except Exception as e:
        logger.warning(f"_switch_to_next error: {e}")


AlgorithmFn = Callable[[TrafficLight, object, float, float], None]

ALGORITHM_MAP: dict[str, AlgorithmFn] = {
    "fixed": fixed_time_controller,
    "actuated": actuated_controller,
    "max_pressure": max_pressure_controller,
    "green_wave": green_wave_controller,
}


def get_controller(algorithm: str) -> AlgorithmFn:
    return ALGORITHM_MAP.get(algorithm, fixed_time_controller)

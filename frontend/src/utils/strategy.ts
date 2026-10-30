import { Strategy, TireCompound, TireStint } from '../types';

/**
 * Normalizes any Strategy object (from backend or frontend) ensuring that
 * stints, pit_laps, compounds, and timing properties are always populated
 * and never undefined.
 */
export function normalizeStrategy(strat: any, totalLaps: number = 78): Strategy {
  if (!strat) {
    const s1 = Math.floor(totalLaps * 0.45);
    return {
      strategy_id: 'default-strat',
      name: `1-Stop (M-H @ Lap ${s1})`,
      stints: [
        { stint_index: 1, compound: 'MEDIUM', start_lap: 1, end_lap: s1, planned_laps: s1 },
        { stint_index: 2, compound: 'HARD', start_lap: s1 + 1, end_lap: totalLaps, planned_laps: totalLaps - s1 },
      ],
      pit_laps: [s1],
      compounds: ['MEDIUM', 'HARD'],
      expected_time: 5502.4,
      time_std: 12.6,
      risk_score: 1.8,
      win_probability: 0.68,
    };
  }

  // Determine initial compound
  let initialCompound: TireCompound = 'MEDIUM';
  if (strat.initial_compound) {
    initialCompound = strat.initial_compound;
  } else if (Array.isArray(strat.compounds) && strat.compounds.length > 0) {
    initialCompound = strat.compounds[0];
  } else if (Array.isArray(strat.stints) && strat.stints.length > 0) {
    initialCompound = strat.stints[0].compound;
  }

  // Extract pit stops / pit laps
  let pitStops: Array<{ lap: number; compound: TireCompound }> = [];
  if (Array.isArray(strat.pit_stops) && strat.pit_stops.length > 0) {
    pitStops = [...strat.pit_stops].sort((a, b) => a.lap - b.lap);
  } else if (Array.isArray(strat.pit_laps) && strat.pit_laps.length > 0) {
    const comps = Array.isArray(strat.compounds) ? strat.compounds.slice(1) : [];
    pitStops = strat.pit_laps.map((lap: number, idx: number) => ({
      lap,
      compound: comps[idx] || (idx % 2 === 0 ? 'HARD' : 'MEDIUM'),
    }));
  }

  const pit_laps = pitStops.map((ps) => ps.lap);
  const compounds: TireCompound[] = [initialCompound, ...pitStops.map((ps) => ps.compound)];

  // Build stints
  let stints: TireStint[] = [];
  if (Array.isArray(strat.stints) && strat.stints.length > 0) {
    stints = strat.stints.map((s: any, idx: number) => ({
      stint_index: s.stint_index || idx + 1,
      compound: s.compound || compounds[idx] || 'MEDIUM',
      start_lap: s.start_lap || 1,
      end_lap: s.end_lap || totalLaps,
      planned_laps: s.planned_laps || (s.end_lap - s.start_lap + 1) || totalLaps,
    }));
  } else {
    let prevLap = 0;
    let curComp = initialCompound;
    for (let i = 0; i < pitStops.length; i++) {
      const pitLap = Math.min(totalLaps, pitStops[i].lap);
      if (pitLap > prevLap) {
        stints.push({
          stint_index: stints.length + 1,
          compound: curComp,
          start_lap: prevLap + 1,
          end_lap: pitLap,
          planned_laps: pitLap - prevLap,
        });
      }
      prevLap = pitLap;
      curComp = pitStops[i].compound;
    }
    if (prevLap < totalLaps) {
      stints.push({
        stint_index: stints.length + 1,
        compound: curComp,
        start_lap: prevLap + 1,
        end_lap: totalLaps,
        planned_laps: totalLaps - prevLap,
      });
    }
  }

  // Ensure at least one stint exists
  if (stints.length === 0) {
    stints.push({
      stint_index: 1,
      compound: initialCompound,
      start_lap: 1,
      end_lap: totalLaps,
      planned_laps: totalLaps,
    });
  }

  return {
    strategy_id: strat.strategy_id || `strat-${Date.now()}`,
    name: strat.name || `${pit_laps.length}-Stop (${compounds.map((c) => c[0]).join('-')})`,
    stints,
    pit_laps,
    compounds,
    expected_time: typeof strat.expected_time === 'number' ? strat.expected_time : 5502.4,
    time_std: typeof strat.time_std === 'number' ? strat.time_std : 12.6,
    risk_score: typeof strat.risk_score === 'number' ? strat.risk_score : 1.8,
    win_probability: typeof strat.win_probability === 'number' ? strat.win_probability : 0.68,
  };
}


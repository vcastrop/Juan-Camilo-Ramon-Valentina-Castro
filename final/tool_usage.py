"""Telemetry derived only from saved execution traces, never answer text or gold."""


def metrics(record):
    trace=record.get('tool_trace',[])
    if not isinstance(trace,list):trace=[]
    trace=[event for event in trace if isinstance(event,dict)]
    results=[event['tool_result'] for event in trace if isinstance(event.get('tool_result'),dict)]
    successes=sum(result.get('ok') is True for result in results)
    return {'router_used':bool(trace),
            'tool_requested':any(isinstance(event.get('decision'),dict) and event['decision'].get('action')=='tool' for event in trace),
            'tool_result_recorded':bool(results),'tool_success':successes>0,'successful_tool_results':successes}


def summarize(rows):
    observations=[metrics(row['record']) for row in rows]
    return {'case_count':len(rows),'router_cases':sum(m['router_used'] for m in observations),
            'tool_requested_cases':sum(m['tool_requested'] for m in observations),
            'tool_result_cases':sum(m['tool_result_recorded'] for m in observations),
            'successful_tool_cases':sum(m['tool_success'] for m in observations),
            'successful_tool_results':sum(m['successful_tool_results'] for m in observations),
            'definition':'Router activity is not tool execution. A recorded failed/blocked result is not successful execution. No inference from answer text.'}

"""把最终文本包装成 DeepSeek/OpenAI Responses API 的 SSE 事件流。

网页端请求是 stream=true;一次性把全文放在一个 delta 里发出即可(网页只是累积文本)。
事件序列按 OpenAI Responses API 标准:created → output_item.added → content_part.added
→ output_text.delta → output_text.done → content_part.done → output_item.done → completed。
若联调发现网页认的事件名不同,只改本文件。
"""
import json
import time
import uuid


def _rid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:24]}"


def stream_events(text: str, model: str = "illustration-gateway"):
    """生成 SSE 帧(字符串)。用法:for frame in stream_events(...) yield frame"""
    resp_id = _rid("resp")
    item_id = _rid("msg")
    created = int(time.time())

    def frame(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    response_skeleton = {
        "id": resp_id,
        "object": "response",
        "created_at": created,
        "model": model,
        "status": "in_progress",
        "output": [],
    }

    frames = [
        frame("response.created", {"type": "response.created", "response": response_skeleton}),
        frame("response.in_progress", {"type": "response.in_progress", "response": response_skeleton}),
        frame("response.output_item.added", {
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {"id": item_id, "type": "message", "status": "in_progress",
                     "role": "assistant", "content": []},
        }),
        frame("response.content_part.added", {
            "type": "response.content_part.added",
            "item_id": item_id, "output_index": 0, "content_index": 0,
            "part": {"type": "output_text", "text": ""},
        }),
        frame("response.output_text.delta", {
            "type": "response.output_text.delta",
            "item_id": item_id, "output_index": 0, "content_index": 0,
            "delta": text,
        }),
        frame("response.output_text.done", {
            "type": "response.output_text.done",
            "item_id": item_id, "output_index": 0, "content_index": 0,
            "text": text,
        }),
        frame("response.content_part.done", {
            "type": "response.content_part.done",
            "item_id": item_id, "output_index": 0, "content_index": 0,
            "part": {"type": "output_text", "text": text},
        }),
        frame("response.output_item.done", {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": {"id": item_id, "type": "message", "status": "completed",
                     "role": "assistant",
                     "content": [{"type": "output_text", "text": text}]},
        }),
        frame("response.completed", {
            "type": "response.completed",
            "response": {
                **response_skeleton,
                "status": "completed",
                "output": [{"id": item_id, "type": "message", "status": "completed",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": text}]}],
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            },
        }),
    ]
    return frames


def non_stream_response(text: str, model: str = "illustration-gateway") -> dict:
    """stream=false 时的一次性 JSON 响应。"""
    return {
        "id": _rid("resp"),
        "object": "response",
        "created_at": int(time.time()),
        "model": model,
        "status": "completed",
        "output": [{
            "id": _rid("msg"), "type": "message", "status": "completed",
            "role": "assistant",
            "content": [{"type": "output_text", "text": text}],
        }],
        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    }


# ============ Chat Completions API 格式 ============
# 网页端若走 /chat/completions(messages 数组),响应用 chat.completion.chunk 流

def chat_stream_events(text: str, model: str = "illustration-gateway") -> list[str]:
    """Chat Completions SSE 帧序列,以 [DONE] 收尾。"""
    cid = _rid("chatcmpl")
    created = int(time.time())

    def chunk(delta: dict, finish: str | None = None) -> str:
        data = {
            "id": cid, "object": "chat.completion.chunk", "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    return [
        chunk({"role": "assistant", "content": ""}),
        chunk({"content": text}),
        chunk({}, "stop"),
        "data: [DONE]\n\n",
    ]


def chat_non_stream_response(text: str, model: str = "illustration-gateway") -> dict:
    return {
        "id": _rid("chatcmpl"),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": text},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

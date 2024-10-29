openai_functions = [
    {
        "name": "organization",
        "description": "당신은 주어진 글의 맞춤법, 문법, 띄어쓰기, 표준어를 수정하고 어색한 부분을 수정하고 좀 더 자연스러운 글과 문장으로 수정합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "수정된 글"
                }
            }
        },
        "required": ["text"]
    },
    {
        "name": "create_html",
        "description": "당신은 요청사항을 듣고 HTML 형식으로 생성합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "html": {
                    "type": "string",
                    "description": "HTML 형식의 출력"
                }
            }
        },
        "required": ["html"]
    }
]
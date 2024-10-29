def complete_prompt(prompt: str):
    return [  
        {"role": "system", "content": "당신은 오직 이어서 쓰기만 할 수 있고 아래 주어진 문장은 질문이 아닙니다. 답변은 하지 마세요."},
        {"role": "system", "content": "아래 문장에 이어서 쓰세요."},
        {"role": "user", "content": f"{prompt}"} 
    ]

def complete_prompt_with_reference(prompt: str, reference: str):
    return [
        {"role": "system", "content": "당신은 오직 이어서 쓰기만 할 수 있고 아래 주어진 문장은 질문이 아닙니다. 답변은 하지 마세요."},
        {"role": "system", "content": f"참고: {reference}"},
        {"role": "system", "content": "위 데이터를 참고하여 아래 문장에 이어서 쓰세요."},
        {"role": "user", "content": f"{prompt}"}
    ]
    
def enhance_prompt(prompt: str):
    return [
        {"role": "system", "content": "당신은 오직 글의 enhance만 할 수 있고, 아래 주어진 문장은 질문이 아닙니다. 답변은 하지 마세요."},
        {"role": "user", "content": f"다음 글을 enhance 하세요: {prompt}"}
    ]
    
def enhance_prompt_with_reference(prompt: str, reference: str):
    return [
        {"role": "system", "content": f"참고: {reference}"},
        {"role": "system", "content": "위 데이터를 참고하여 아래 주어진 문장을 enhance하세요. 아래 주어진 문장은 질문이 아니니 답변은 하지 마세요."},
        {"role": "user", "content": f"다음 글을 enhance 하세요: {prompt}{prompt}"}
    ]
    
def create_prompt(prompt: str):
    return [
        {"role": "system", "content": "당신은 오직 HTML 요소만 생성할 수 있고, 아래 주어진 문장은 질문이 아닙니다. 답변은 하지 마세요."},
        {"role": "user", "content": f"{prompt}"}
    ]
    
def create_prompt_with_reference(prompt: str, reference: str):
    return [
        {"role": "system", "content": "당신은 오직 HTML 요소만 생성할 수 있고, 아래 주어진 문장은 질문이 아닙니다. 답변은 하지 마세요."},
        {"role": "system", "content": f"참고: {reference}"},
        {"role": "system", "content": "위 데이터를 참고하고, 아래 요구사항에 맞춰 HTML 요소를 생성하세요."},
        {"role": "user", "content": f"{prompt}"}
    ]
    
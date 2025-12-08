# aiapi.py
from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# Ollama 配置
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_DEFAULT_MODEL', 'llama2')

def get_ollama_models():
    """获取可用的 Ollama 模型列表"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return []

def generate_response(messages, model=DEFAULT_MODEL, stream=False):
    """
    调用 Ollama API 生成回复
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    
    # 构建请求数据
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            stream=stream,
            timeout=60
        )
        response.raise_for_status()
        
        if stream:
            return response.iter_lines()
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API 调用失败: {str(e)}")
        raise e

@app.route('/api/chat', methods=['POST'])
def chat_completion():
    """
    聊天补全接口
    """
    try:
        data = request.json
        
        # 验证必要参数
        if not data or 'message' not in data:
            return jsonify({
                'error': '缺少必要参数: message',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        model = data.get('model', DEFAULT_MODEL)
        system_prompt = data.get('system_prompt', '你是一个有用的助手。')
        conversation_history = data.get('history', [])
        stream = data.get('stream', False)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话
        for msg in conversation_history:
            if 'role' in msg and 'content' in msg:
                messages.append(msg)
        
        # 添加当前消息
        messages.append({"role": "user", "content": user_message})
        
        # 流式响应
        if stream:
            def generate():
                try:
                    for line in generate_response(messages, model, stream=True):
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data_str = line[6:]  # 去掉 'data: ' 前缀
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data_obj = json.loads(data_str)
                                    if 'message' in data_obj and 'content' in data_obj['message']:
                                        content = data_obj['message']['content']
                                        yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                                except json.JSONDecodeError:
                                    continue
                    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
                except Exception as e:
                    error_msg = f"流式响应错误: {str(e)}"
                    yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"
            
            return app.response_class(
                stream_with_context(generate()),
                mimetype='text/plain'
            )
        
        # 非流式响应
        else:
            response_data = generate_response(messages, model, stream=False)
            
            if 'message' in response_data and 'content' in response_data['message']:
                ai_response = response_data['message']['content']
                
                logger.info(f"用户消息: {user_message[:50]}...")
                logger.info(f"AI回复: {ai_response[:50]}...")
                
                return jsonify({
                    'response': ai_response,
                    'status': 'success',
                    'model': model
                })
            else:
                return jsonify({
                    'error': 'Ollama 响应格式异常',
                    'status': 'error'
                }), 500
        
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        return jsonify({
            'error': f'服务器内部错误: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """
    获取可用的模型列表
    """
    try:
        models = get_ollama_models()
        return jsonify({
            'models': models,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_text():
    """
    文本生成接口（兼容旧版 Ollama API）
    """
    try:
        data = request.json
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': '缺少必要参数: prompt',
                'status': 'error'
            }), 400
        
        prompt = data['prompt']
        model = data.get('model', DEFAULT_MODEL)
        
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        return jsonify({
            'response': response_data.get('response', ''),
            'status': 'success',
            'model': model
        })
        
    except Exception as e:
        logger.error(f"文本生成错误: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/pull-model', methods=['POST'])
def pull_model():
    """
    拉取新模型到 Ollama
    """
    try:
        data = request.json
        
        if not data or 'model_name' not in data:
            return jsonify({
                'error': '缺少必要参数: model_name',
                'status': 'error'
            }), 400
        
        model_name = data['model_name']
        url = f"{OLLAMA_BASE_URL}/api/pull"
        payload = {
            "name": model_name,
            "stream": False
        }
        
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        # 处理流式响应
        result = ""
        for line in response.iter_lines():
            if line:
                line_data = json.loads(line)
                if 'status' in line_data:
                    result += line_data['status'] + "\n"
        
        return jsonify({
            'status': 'success',
            'message': f'模型 {model_name} 拉取完成',
            'details': result
        })
        
    except Exception as e:
        logger.error(f"拉取模型错误: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    try:
        # 检查 Ollama 服务是否可用
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        ollama_status = "healthy" if response.status_code == 200 else "unhealthy"
        
        return jsonify({
            'status': 'healthy',
            'service': 'Ollama AI API',
            'ollama_service': ollama_status,
            'available_models': len(get_ollama_models())
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'Ollama AI API',
            'ollama_service': 'unreachable',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    # 启动时检查 Ollama 服务
    try:
        models = get_ollama_models()
        logger.info(f"Ollama 服务可用，已加载模型: {models}")
    except Exception as e:
        logger.warning(f"无法连接到 Ollama 服务: {e}")
        logger.info("请确保 Ollama 已在 http://localhost:11434 运行")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
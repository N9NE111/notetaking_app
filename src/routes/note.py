from flask import Blueprint, request, jsonify
from src.models.note import Note
from src.database import db
from datetime import datetime, date, time
import random

note_bp = Blueprint('note', __name__)

@note_bp.route('/', methods=['GET'])
def get_notes():
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        notes = Note.query.filter(
            db.or_(
                Note.title.contains(search_query),
                Note.content.contains(search_query),
                Note.tags.contains(search_query)
            )
        ).order_by(Note.updated_at.desc()).all()
    else:
        notes = Note.query.order_by(Note.updated_at.desc()).all()
    
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/', methods=['POST'])
def create_note():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    event_date = None
    event_time = None
    
    if data.get('event_date'):
        try:
            event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '事件日期格式错误'}), 400
    
    if data.get('event_time'):
        try:
            event_time = datetime.strptime(data['event_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': '事件时间格式错误'}), 400
    
    note = Note(
        title=data['title'],
        content=data['content'],
        tags=data.get('tags', ''),
        event_date=event_date,
        event_time=event_time
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201

@note_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    if 'tags' in data:
        note.tags = data['tags']
    
    if 'event_date' in data:
        if data['event_date']:
            try:
                note.event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '事件日期格式错误'}), 400
        else:
            note.event_date = None
    
    if 'event_time' in data:
        if data['event_time']:
            try:
                note.event_time = datetime.strptime(data['event_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': '事件时间格式错误'}), 400
        else:
            note.event_time = None
    
    note.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(note.to_dict())

@note_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': '笔记已删除'}), 200

@note_bp.route('/generate', methods=['POST'])
def generate_note():
    data = request.get_json()
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({'error': '请提供主题'}), 400
    
    ai_templates = [
        f"关于{topic}的重要要点：\n\n1. 基础概念\n2. 实践应用\n3. 注意事项\n4. 相关资源",
        f"{topic}学习笔记：\n\n• 核心知识点\n• 常见问题\n• 解决方案\n• 扩展阅读",
        f"{topic}备忘清单：\n\n✓ 准备工作\n✓ 执行步骤\n✓ 检查要点\n✓ 后续跟进"
    ]
    
    generated_content = random.choice(ai_templates)
    
    note = Note(
        title=f"AI生成: {topic}",
        content=generated_content,
        tags=f"ai-generated, {topic.lower()}"
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201

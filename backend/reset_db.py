import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.api.models import User

def reset_database():
    app = create_app()
    
    with app.app_context():
        # 删除所有表
        print("正在删除所有表...")
        db.drop_all()
        
        # 创建所有表
        print("正在创建所有表...")
        db.create_all()
        
        # 创建初始用户
        print("正在创建初始用户...")
        
        # 普通用户 zyx / zyx123
        user = User(username='zyx', email='zyx@example.com')
        user.set_password('zyx123')
        db.session.add(user)
        
        # 管理员 admin / admin123
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 提交更改
        db.session.commit()
        
        print("数据库重置完成!")
        print("初始用户信息:")
        print("  普通用户: zyx / zyx123")
        print("  管理员: admin / admin123")

if __name__ == '__main__':
    reset_database()
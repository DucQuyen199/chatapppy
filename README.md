```markdown:readme.md
# Real-time Chat Application

Ứng dụng chat realtime được xây dựng bằng Flask và SQL Server, hỗ trợ giao tiếp trực tuyến giữa người dùng.

## Tính năng

- Đăng ký và đăng nhập người dùng
- Chat realtime 1-1
- Hiển thị trạng thái online/offline
- Tìm kiếm người dùng
- Thông báo tin nhắn mới
- Lịch sử chat
- Giao diện thân thiện với người dùng

## Yêu cầu hệ thống

- Python 3.8+
- SQL Server 2019+
- ODBC Driver 17 for SQL Server

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd chat-app
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Cấu hình SQL Server:
- Đảm bảo SQL Server đang chạy
- Cập nhật thông tin kết nối trong file .env:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=mssql+pyodbc://sa:@Ducquyenbg123@localhost/chatapp?driver=ODBC+Driver+17+for+SQL+Server
```

4. Khởi tạo database:
```bash
sqlcmd -S localhost -U sa -P your-password -i data.sql
```

5. Chạy ứng dụng:
```bash
python run.py
```

Ứng dụng sẽ chạy tại http://localhost:5001

## Cấu trúc project

```
chat-app/
├── app.py              # Flask application
├── config.py           # Cấu hình ứng dụng
├── models.py           # Database models
├── data.sql           # SQL schema
├── requirements.txt    # Python dependencies
├── run.py             # Entry point
├── static/            # Static files
└── templates/         # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    └── chat.html
```

## Công nghệ sử dụng

- **Backend**: Flask, SQLAlchemy, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQL Server
- **Real-time Communication**: Socket.IO
- **Authentication**: Flask-Login

## Tính năng chi tiết

1. **Xác thực người dùng**
   - Đăng ký tài khoản mới
   - Đăng nhập/Đăng xuất
   - Mật khẩu được mã hóa

2. **Chat realtime**
   - Gửi và nhận tin nhắn ngay lập tức
   - Hiển thị trạng thái tin nhắn
   - Tự động cuộn đến tin nhắn mới nhất

3. **Quản lý người dùng**
   - Hiển thị danh sách người dùng
   - Tìm kiếm người dùng
   - Hiển thị trạng thái online/offline

4. **Giao diện**
   - Responsive design
   - Giao diện chat thân thiện
   - Hiển thị thời gian tin nhắn
   - Phân biệt tin nhắn gửi/nhận

## Bảo mật

- Mật khẩu được mã hóa bằng Werkzeug
- Xác thực người dùng bắt buộc
- Bảo vệ chống SQL injection
- CSRF protection

## Đóng góp

Mọi đóng góp đều được chào đón. Vui lòng:
1. Fork project
2. Tạo branch mới
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License

## Tác giả

Nguyen Quyen

## Hỗ trợ

Nếu bạn gặp vấn đề, vui lòng tạo issue trong repository.
```

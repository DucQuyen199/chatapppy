-- Đảm bảo user sa có quyền truy cập
USE [master]
GO
ALTER LOGIN [sa] WITH PASSWORD=N'@Ducquyenbg123'
GO
ALTER LOGIN [sa] ENABLE
GO

-- Tạo database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'chatapp')
BEGIN
    CREATE DATABASE chatapp;
END
GO

USE chatapp;
GO

-- Cấp quyền cho sa trên database chatapp
ALTER AUTHORIZATION ON DATABASE::chatapp TO sa;
GO

-- Xóa các bảng cũ nếu tồn tại
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[chat_messages]'))
    DROP TABLE chat_messages;
GO

IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]'))
    DROP TABLE users;
GO

-- Xóa các stored procedure cũ
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'GetChatHistory')
    DROP PROCEDURE GetChatHistory;
GO

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'GetUnreadMessages')
    DROP PROCEDURE GetUnreadMessages;
GO

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'MarkMessagesAsRead')
    DROP PROCEDURE MarkMessagesAsRead;
GO

-- Xóa trigger cũ
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_UpdateLastSeen')
    DROP TRIGGER TR_UpdateLastSeen;
GO

-- Tạo bảng users
CREATE TABLE users (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(100),
    status NVARCHAR(20),
    last_seen DATETIME2
);
GO

-- Tạo bảng chat_messages
CREATE TABLE chat_messages (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    content NVARCHAR(4000) NOT NULL,
    sender_id BIGINT NOT NULL,
    receiver_id BIGINT NOT NULL,
    type NVARCHAR(20) NOT NULL,
    timestamp DATETIME2 NOT NULL,
    is_read BIT DEFAULT 0,
    CONSTRAINT FK_ChatMessage_Sender FOREIGN KEY (sender_id) REFERENCES users(id),
    CONSTRAINT FK_ChatMessage_Receiver FOREIGN KEY (receiver_id) REFERENCES users(id)
);
GO

-- Tạo indexes
CREATE INDEX IX_Users_Username ON users(username);
CREATE INDEX IX_ChatMessages_Sender ON chat_messages(sender_id);
CREATE INDEX IX_ChatMessages_Receiver ON chat_messages(receiver_id);
CREATE INDEX IX_ChatMessages_Timestamp ON chat_messages(timestamp);
GO

-- Tạo stored procedure để lấy lịch sử chat
CREATE PROCEDURE GetChatHistory
    @SenderId BIGINT,
    @ReceiverId BIGINT
AS
BEGIN
    SELECT m.*, 
           s.username as sender_username,
           r.username as receiver_username
    FROM chat_messages m
    INNER JOIN users s ON m.sender_id = s.id
    INNER JOIN users r ON m.receiver_id = r.id
    WHERE (m.sender_id = @SenderId AND m.receiver_id = @ReceiverId)
       OR (m.sender_id = @ReceiverId AND m.receiver_id = @SenderId)
    ORDER BY m.timestamp DESC;
END
GO

-- Tạo stored procedure để lấy tin nhắn chưa đọc
CREATE PROCEDURE GetUnreadMessages
    @UserId BIGINT
AS
BEGIN
    SELECT m.*, 
           s.username as sender_username,
           r.username as receiver_username
    FROM chat_messages m
    INNER JOIN users s ON m.sender_id = s.id
    INNER JOIN users r ON m.receiver_id = r.id
    WHERE m.receiver_id = @UserId 
    AND m.is_read = 0
    ORDER BY m.timestamp DESC;
END
GO

-- Tạo stored procedure để đánh dấu tin nhắn đã đọc
CREATE PROCEDURE MarkMessagesAsRead
    @ReceiverId BIGINT,
    @SenderId BIGINT
AS
BEGIN
    UPDATE chat_messages
    SET is_read = 1
    WHERE receiver_id = @ReceiverId
    AND sender_id = @SenderId
    AND is_read = 0;
END
GO

-- Tạo stored procedure để thêm tin nhắn mới
CREATE OR ALTER PROCEDURE InsertChatMessage
    @Content NVARCHAR(4000),
    @SenderId BIGINT,
    @ReceiverId BIGINT,
    @Type NVARCHAR(20),
    @Timestamp DATETIME2,
    @IsRead BIT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Insert message và lấy ID
    DECLARE @NewMessageId BIGINT;
    
    INSERT INTO chat_messages (content, sender_id, receiver_id, type, timestamp, is_read)
    VALUES (@Content, @SenderId, @ReceiverId, @Type, @Timestamp, @IsRead);
    
    SET @NewMessageId = SCOPE_IDENTITY();
    
    -- Cập nhật trạng thái người dùng
    UPDATE users
    SET last_seen = GETDATE(),
        status = 'ONLINE'
    WHERE id = @SenderId;
    
    -- Trả về ID của tin nhắn mới
    SELECT @NewMessageId AS id;
END
GO 
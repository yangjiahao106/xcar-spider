# 创建表 cars

create table cars
(
id      int auto_increment  not null primary key,   # 主键
name    varchar(20)         not null,               # 车名
brand   varchar(20)         not null,               # 品牌
level   varchar(20)         null,                   # 级别
star    float               null                    # 评分 /5分
);
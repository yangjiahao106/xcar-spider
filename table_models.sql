# 创建表 models

create table models(
id              int         not null auto_increment primary key,
model           varchar(30) not null,   # 型号
gearbox         varchar(20) null,       # 变速箱
motor           varchar(20) null,       # 发动机
power           int         null,       # 功率 KW
guiding_price   float       null,       # 指导价 /万
seater          int         null,       # 座位数
oil_consumption float       null,       # 油耗 L/100km
car_id          int         not null,
foreign key(car_id) references cars(id)
);

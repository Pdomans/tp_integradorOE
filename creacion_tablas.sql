-- crear la tabla 
create database BOT
use  bot 
go

--CREACION DE TABLAS ( normalizacion 3) 

--tabla sectores 
create table sectores  (

idsector int identity (1,1) primary key,
nombresector varchar(100) not null

)

--tabla de usuarios 
create table  usuarios (

idusuario  int not null primary key,
nombre  varchar (100) not null,
idsector int not null, 
activo bit  not null default 1,
foreign key (idsector) references sectores(idsector)

)

--categorias 
create table  categorias (
idcategoria int  not null primary key, 
nombrecategoria varchar (100) not null

)


-- impacto 
create table impacto (
idimpacto int not null primary key , 
nombreimpacto varchar (100) not null 
)


--estados de tickets 
create table estadosticket(
idestado int not null primary key, 
nombreestado varchar (50) not null
)



--creacion de la able tickets 

create table  tickets (
idticket int identity(1,1) primary key,
nroticket varchar(20) not null,
legajo  int not null, 
idcategoria int not null, 
idimpacto int not null,
idestado int not null, 
descripcion varchar (max) not null,
fechacreacion datetime not null default getdate(),
FechaCierre datetime null,
Observaciones varchar(max) NULL

foreign key (legajo)
references usuarios(idusuario),

foreign key (idcategoria)
references categorias(idcategoria),

foreign key (idimpacto)
references impacto(idimpacto),

foreign key (idestado)
references estadosticket(idestado)
)



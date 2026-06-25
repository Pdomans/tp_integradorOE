use [BOT]

--carga de  usuarios 

insert into usuarios
(idusuario,nombre,idsector,activo)
values 
(1001,'Pablo doma',1,1),
(1002,'Luaciano doma ',2,1),
(1003,'Federico doma',1,1);


--sectores 
insert into sectores
(nombresector)
VALUES 
('Sistemas'),
('RRHH'),
('Administracion'),
('Ventas');


-- carga de categorias 
insert into categorias
(idcategoria,nombrecategoria)
values
(1,'Hardware'),
(2,'Software'),
(3,'Redes'),
(4,'Impresoras'),
(5,'Accesos'),
(6,'Navision'),
(7,'Newcom'),
(8,'Otros');

--impacto de ticekt 
insert into  impacto 
(idimpacto,nombreimpacto)
values
(1,'bajo'),
(2,'medio'),
(3,'alto');


--estado de ticket 

insert into estadosticket
(idestado,nombreestado)
values
(1,'Abierto'),
(2,'En Proceso'),
(3,'Resuelto'),
(4,'Cerrado');

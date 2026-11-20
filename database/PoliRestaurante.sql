/* =============================================================================
   PoliRestaurante - Script de creación de la base de datos (SQL Server / T-SQL)
   ============================================================================= */
USE master;
GO

IF DB_ID(N'PoliRestaurante') IS NULL
    CREATE DATABASE PoliRestaurante;
GO

USE PoliRestaurante;
GO

SET NOCOUNT ON;
GO

/* ------------------------------------------------------------------ Mesa */
IF OBJECT_ID(N'dbo.Mesa', N'U') IS NULL
CREATE TABLE dbo.Mesa (
    id_mesa     INT IDENTITY(1,1) NOT NULL,
    numero      INT           NOT NULL,
    capacidad   INT           NOT NULL,
    estado      NVARCHAR(10)  NOT NULL CONSTRAINT DF_Mesa_estado DEFAULT N'LIBRE',
    CONSTRAINT PK_Mesa PRIMARY KEY (id_mesa),
    CONSTRAINT UQ_Mesa_numero UNIQUE (numero),
    CONSTRAINT CK_Mesa_capacidad CHECK (capacidad > 0),
    CONSTRAINT CK_Mesa_estado CHECK (estado IN (N'LIBRE', N'OCUPADA'))
);
GO

/* -------------------------------------------------------------- Producto */
IF OBJECT_ID(N'dbo.Producto', N'U') IS NULL
CREATE TABLE dbo.Producto (
    id_producto INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)  NOT NULL,
    descripcion NVARCHAR(MAX)  NULL,          -- incluye los ingredientes (HU14)
    precio      DECIMAL(10,2)  NOT NULL,
    tipo        NVARCHAR(10)   NOT NULL,
    imagen      NVARCHAR(255)  NULL,
    disponible  BIT            NOT NULL CONSTRAINT DF_Producto_disponible DEFAULT 1,
    CONSTRAINT PK_Producto PRIMARY KEY (id_producto),
    CONSTRAINT CK_Producto_precio CHECK (precio > 0),
    CONSTRAINT CK_Producto_tipo CHECK (tipo IN (N'PLATO', N'BEBIDA'))
);
GO

/* --------------------------------------------------------- Administrador */
IF OBJECT_ID(N'dbo.Administrador', N'U') IS NULL
CREATE TABLE dbo.Administrador (
    id_usuario  INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)  NOT NULL,
    correo      NVARCHAR(150)  NOT NULL,
    contrasena  NVARCHAR(255)  NOT NULL,      -- hash, nunca texto plano
    telefono    NVARCHAR(MAX)  NULL,
    rol         NVARCHAR(20)   NOT NULL CONSTRAINT DF_Administrador_rol DEFAULT N'ADMINISTRADOR',
    CONSTRAINT PK_Administrador PRIMARY KEY (id_usuario),
    CONSTRAINT UQ_Administrador_correo UNIQUE (correo),
    CONSTRAINT CK_Administrador_rol CHECK (rol = N'ADMINISTRADOR')
);
GO

/* --------------------------------------------------------------- Mesero */
IF OBJECT_ID(N'dbo.Mesero', N'U') IS NULL
CREATE TABLE dbo.Mesero (
    id_usuario  INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)  NOT NULL,
    correo      NVARCHAR(150)  NOT NULL,
    contrasena  NVARCHAR(255)  NOT NULL,
    telefono    NVARCHAR(MAX)  NULL,
    rol         NVARCHAR(20)   NOT NULL CONSTRAINT DF_Mesero_rol DEFAULT N'MESERO',
    CONSTRAINT PK_Mesero PRIMARY KEY (id_usuario),
    CONSTRAINT UQ_Mesero_correo UNIQUE (correo),
    CONSTRAINT CK_Mesero_rol CHECK (rol = N'MESERO')
);
GO

/* --------------------------------------------------------------- Cocina */
IF OBJECT_ID(N'dbo.Cocina', N'U') IS NULL
CREATE TABLE dbo.Cocina (
    id_usuario  INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)  NOT NULL,
    correo      NVARCHAR(150)  NOT NULL,
    contrasena  NVARCHAR(255)  NOT NULL,
    telefono    NVARCHAR(MAX)  NULL,
    rol         NVARCHAR(20)   NOT NULL CONSTRAINT DF_Cocina_rol DEFAULT N'COCINA',
    CONSTRAINT PK_Cocina PRIMARY KEY (id_usuario),
    CONSTRAINT UQ_Cocina_correo UNIQUE (correo),
    CONSTRAINT CK_Cocina_rol CHECK (rol = N'COCINA')
);
GO

/* -------------------------------------------------------------- Cliente */
IF OBJECT_ID(N'dbo.Cliente', N'U') IS NULL
CREATE TABLE dbo.Cliente (
    id_usuario  INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)  NOT NULL,
    correo      NVARCHAR(150)  NOT NULL,
    contrasena  NVARCHAR(255)  NOT NULL,
    telefono    NVARCHAR(MAX)  NULL,
    rol         NVARCHAR(20)   NOT NULL CONSTRAINT DF_Cliente_rol DEFAULT N'CLIENTE',
    CONSTRAINT PK_Cliente PRIMARY KEY (id_usuario),
    CONSTRAINT UQ_Cliente_correo UNIQUE (correo),
    CONSTRAINT CK_Cliente_rol CHECK (rol = N'CLIENTE')
);
GO

/* --------------------------------------------------------------- Pedido */
IF OBJECT_ID(N'dbo.Pedido', N'U') IS NULL
CREATE TABLE dbo.Pedido (
    id_pedido    INT IDENTITY(1,1) NOT NULL,
    id_mesero    INT            NULL,
    id_cocina    INT            NOT NULL,
    id_cliente   INT            NOT NULL,
    id_mesa      INT            NULL,
    fecha        DATETIME       NOT NULL CONSTRAINT DF_Pedido_fecha DEFAULT GETDATE(),
    fecha_estado DATETIME       NOT NULL CONSTRAINT DF_Pedido_fecha_estado DEFAULT GETDATE(),
    tipo_pedido  NVARCHAR(10)   NOT NULL,
    direccion    NVARCHAR(255)  NULL,
    estado       NVARCHAR(20)   NOT NULL CONSTRAINT DF_Pedido_estado DEFAULT N'PENDIENTE',
    pagado       BIT            NOT NULL CONSTRAINT DF_Pedido_pagado DEFAULT 0,
    medio_pago   NVARCHAR(50)   NULL,
    total        DECIMAL(10,2)  NOT NULL CONSTRAINT DF_Pedido_total DEFAULT 0,
    CONSTRAINT PK_Pedido PRIMARY KEY (id_pedido),
    CONSTRAINT FK_Pedido_Mesero  FOREIGN KEY (id_mesero)  REFERENCES dbo.Mesero (id_usuario),
    CONSTRAINT FK_Pedido_Cocina  FOREIGN KEY (id_cocina)  REFERENCES dbo.Cocina (id_usuario),
    CONSTRAINT FK_Pedido_Cliente FOREIGN KEY (id_cliente) REFERENCES dbo.Cliente (id_usuario),
    CONSTRAINT FK_Pedido_Mesa    FOREIGN KEY (id_mesa)    REFERENCES dbo.Mesa (id_mesa),
    CONSTRAINT CK_Pedido_tipo   CHECK (tipo_pedido IN (N'MESA', N'DOMICILIO')),
    CONSTRAINT CK_Pedido_estado CHECK (estado IN (N'PENDIENTE', N'EN PREPARACION', N'LISTO', N'ENTREGADO', N'CANCELADO')),
    CONSTRAINT CK_Pedido_total  CHECK (total >= 0),
    -- Regla de la fábrica: mesa => mesa y mesero, sin dirección; domicilio => dirección, sin mesa ni mesero.
    CONSTRAINT CK_Pedido_modalidad CHECK (
           (tipo_pedido = N'MESA'      AND id_mesa IS NOT NULL AND id_mesero IS NOT NULL AND direccion IS NULL)
        OR (tipo_pedido = N'DOMICILIO' AND id_mesa IS NULL     AND id_mesero IS NULL     AND direccion IS NOT NULL))
);
GO

/* -------------------------------------------------------- DetallePedido */
IF OBJECT_ID(N'dbo.DetallePedido', N'U') IS NULL
CREATE TABLE dbo.DetallePedido (
    id_pedido       INT           NOT NULL,
    id_producto     INT           NOT NULL,
    cantidad        INT           NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,   -- precio vigente cuando se hizo el pedido
    CONSTRAINT PK_DetallePedido PRIMARY KEY (id_pedido, id_producto),
    CONSTRAINT FK_DetallePedido_Pedido   FOREIGN KEY (id_pedido)   REFERENCES dbo.Pedido (id_pedido),
    CONSTRAINT FK_DetallePedido_Producto FOREIGN KEY (id_producto) REFERENCES dbo.Producto (id_producto),
    CONSTRAINT CK_DetallePedido_cantidad CHECK (cantidad > 0),
    CONSTRAINT CK_DetallePedido_precio   CHECK (precio_unitario >= 0)
);
GO

/* --------------------------------------------------------------- Índices */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Pedido_cliente' AND object_id = OBJECT_ID(N'dbo.Pedido'))
    CREATE INDEX IX_Pedido_cliente ON dbo.Pedido (id_cliente, fecha DESC);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Pedido_mesero' AND object_id = OBJECT_ID(N'dbo.Pedido'))
    CREATE INDEX IX_Pedido_mesero ON dbo.Pedido (id_mesero, fecha DESC);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Pedido_estado' AND object_id = OBJECT_ID(N'dbo.Pedido'))
    CREATE INDEX IX_Pedido_estado ON dbo.Pedido (estado, fecha);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Pedido_mesa' AND object_id = OBJECT_ID(N'dbo.Pedido'))
    CREATE INDEX IX_Pedido_mesa ON dbo.Pedido (id_mesa);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Pedido_fecha' AND object_id = OBJECT_ID(N'dbo.Pedido'))
    CREATE INDEX IX_Pedido_fecha ON dbo.Pedido (fecha);
GO

/* =============================================================================
   DATOS DE PRUEBA
   Credenciales de ejemplo:
       administrador : admin@polirestaurante.com    / Admin123*
       meseros       : mesero1@polirestaurante.com  / Mesero123*   (y mesero2@...)
       cocina        : cocina@polirestaurante.com   / Cocina123*
       cliente       : cliente@polirestaurante.com  / Cliente123*
   Las mesas se crean con id_mesa = numero (1 a 8).
   ============================================================================= */
IF NOT EXISTS (SELECT 1 FROM dbo.Mesa)
    INSERT INTO dbo.Mesa (numero, capacidad, estado) VALUES
        (1, 2, N'LIBRE'), (2, 2, N'LIBRE'), (3, 4, N'LIBRE'), (4, 4, N'LIBRE'),
        (5, 4, N'LIBRE'), (6, 6, N'LIBRE'), (7, 6, N'LIBRE'), (8, 8, N'LIBRE');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Producto)
    INSERT INTO dbo.Producto (nombre, descripcion, precio, tipo, imagen, disponible) VALUES
        (N'Hamburguesa clásica',   N'Hamburguesa de res de 150 g. Ingredientes: pan brioche, carne de res, queso cheddar, lechuga, tomate y salsa de la casa.', 18000, N'PLATO',  NULL, 1),
        (N'Perro caliente especial', N'Salchicha americana con papa fosforito. Ingredientes: pan, salchicha, queso rallado, cebolla caramelizada, salsa rosada y papa fosforito.', 14000, N'PLATO',  NULL, 1),
        (N'Pizza personal',        N'Pizza individual de 25 cm. Ingredientes: masa artesanal, salsa de tomate, queso mozzarella, jamón y champiñones.', 22000, N'PLATO',  NULL, 1),
        (N'Salchipapa',            N'Papas a la francesa con salchicha. Ingredientes: papa, salchicha, queso, salsa de piña y salsa de ajo.', 16000, N'PLATO',  NULL, 1),
        (N'Ensalada César con pollo', N'Ensalada fresca. Ingredientes: lechuga romana, pechuga de pollo a la plancha, crutones, queso parmesano y aderezo césar.', 19000, N'PLATO',  NULL, 1),
        (N'Brownie con helado',    N'Postre caliente. Ingredientes: chocolate, nueces, mantequilla, huevo y helado de vainilla.', 12000, N'PLATO',  NULL, 0),
        (N'Limonada natural',      N'Limonada recién exprimida. Ingredientes: limón, agua, azúcar y hielo.', 6000,  N'BEBIDA', NULL, 1),
        (N'Gaseosa 400 ml',        N'Gaseosa en botella personal. Sabores: cola, naranja o limón.', 4500,  N'BEBIDA', NULL, 1),
        (N'Jugo de mango',         N'Jugo natural. Ingredientes: mango, agua o leche y azúcar (opcional).', 7000,  N'BEBIDA', NULL, 1);
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Administrador)
    INSERT INTO dbo.Administrador (nombre, correo, contrasena, telefono) VALUES
        (N'Administrador PoliRestaurante', N'admin@polirestaurante.com', N'pbkdf2:sha256:1000000$M3AMjgnbpv5fallZ$eadb8f761dccb4f710f1666d1ed66e349532088a672dcc60127c9a41a0592111', N'3000000001');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Mesero)
    INSERT INTO dbo.Mesero (nombre, correo, contrasena, telefono) VALUES
        (N'Laura Gómez',  N'mesero1@polirestaurante.com', N'pbkdf2:sha256:1000000$maeBkCPGoJXpazKL$84ea8536f67e54971ffd54bfbac7ecf34bc611c2a8113f665ff503d3448a4f4e', N'3000000002'),
        (N'Carlos Pérez', N'mesero2@polirestaurante.com', N'pbkdf2:sha256:1000000$maeBkCPGoJXpazKL$84ea8536f67e54971ffd54bfbac7ecf34bc611c2a8113f665ff503d3448a4f4e', N'3000000003');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Cocina)
    INSERT INTO dbo.Cocina (nombre, correo, contrasena, telefono) VALUES
        (N'Cocina principal', N'cocina@polirestaurante.com', N'pbkdf2:sha256:1000000$xWhyYEosJFsknPwm$0e8d6df9bd7d7bd4938773984564283903a82c27aa386b08be60bcfab8e939d7', N'3000000004');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Cliente)
    INSERT INTO dbo.Cliente (nombre, correo, contrasena, telefono) VALUES
        (N'Cliente en mesa',  N'cliente.mesa@polirestaurante.com', N'pbkdf2:sha256:1000000$4n16RCMgZeL2uE4w$234348e26ea22eb96071764c35d17136de72dfda69212e58ffa9f6669e734049',    NULL),
        (N'Cliente de prueba', N'cliente@polirestaurante.com',     N'pbkdf2:sha256:1000000$wMup0YsBn9TzAE2o$eca2af1afe8c218636b8427c728c36069a1a2e7cae3c92fc1134a8bc2ac22710', N'3000000005');
GO

/* Verificación rápida */
SELECT N'Mesa' AS tabla, COUNT(*) AS filas FROM dbo.Mesa
UNION ALL SELECT N'Producto', COUNT(*) FROM dbo.Producto
UNION ALL SELECT N'Administrador', COUNT(*) FROM dbo.Administrador
UNION ALL SELECT N'Mesero', COUNT(*) FROM dbo.Mesero
UNION ALL SELECT N'Cocina', COUNT(*) FROM dbo.Cocina
UNION ALL SELECT N'Cliente', COUNT(*) FROM dbo.Cliente
UNION ALL SELECT N'Pedido', COUNT(*) FROM dbo.Pedido
UNION ALL SELECT N'DetallePedido', COUNT(*) FROM dbo.DetallePedido;
GO


/* =============================================================================
   SEGURIDAD POR ROLES: LOGINs, USERs, GRANTs y DENYs
   ============================================================================= */

/* ---------------------------------------------------------------- LOGINs */
USE master;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'login_autenticacion')
    CREATE LOGIN login_autenticacion WITH PASSWORD = N'Auth2026*PoliR!', DEFAULT_DATABASE = PoliRestaurante;
GO
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'login_administrador')
    CREATE LOGIN login_administrador WITH PASSWORD = N'Admin2026*PoliR!', DEFAULT_DATABASE = PoliRestaurante;
GO
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'login_mesero')
    CREATE LOGIN login_mesero WITH PASSWORD = N'Mesero2026*PoliR!', DEFAULT_DATABASE = PoliRestaurante;
GO
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'login_cocina')
    CREATE LOGIN login_cocina WITH PASSWORD = N'Cocina2026*PoliR!', DEFAULT_DATABASE = PoliRestaurante;
GO
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'login_cliente')
    CREATE LOGIN login_cliente WITH PASSWORD = N'Cliente2026*PoliR!', DEFAULT_DATABASE = PoliRestaurante;
GO

/* ----------------------------------------------------------------- USERs */
USE PoliRestaurante;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'usr_autenticacion')
    CREATE USER usr_autenticacion FOR LOGIN login_autenticacion;
GO
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'usr_administrador')
    CREATE USER usr_administrador FOR LOGIN login_administrador;
GO
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'usr_mesero')
    CREATE USER usr_mesero FOR LOGIN login_mesero;
GO
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'usr_cocina')
    CREATE USER usr_cocina FOR LOGIN login_cocina;
GO
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'usr_cliente')
    CREATE USER usr_cliente FOR LOGIN login_cliente;
GO

/* =========================================================================
   PERMISOS (GRANT y DENY) POR USUARIO
   =========================================================================

   Mapa de permisos efectivos:

   Tabla            | AUTENTICACIÓN | ADMINISTRADOR | MESERO              | COCINA         | CLIENTE
   -----------------+---------------+---------------+---------------------+----------------+---------------------
   Mesa             | —             | CRUD          | SELECT, UPDATE      | SELECT         | SELECT
   Producto         | —             | CRUD          | SELECT              | SELECT         | SELECT
   Administrador    | SELECT        | CRUD          | SELECT              | SELECT         | SELECT
   Mesero           | SELECT        | CRUD          | SELECT              | SELECT         | SELECT
   Cocina           | SELECT        | CRUD          | SELECT              | SELECT         | SELECT
   Cliente          | SELECT        | CRUD          | SELECT              | SELECT         | SELECT, INSERT, UPDATE
   Pedido           | —             | CRUD          | CRUD                | SELECT, UPDATE | CRUD
   DetallePedido    | —             | CRUD          | SELECT, INSERT, DEL | SELECT         | SELECT, INSERT, DEL
   ========================================================================= */

/* ---- usr_autenticacion: solo lectura de tablas de usuarios (pre-login) ---- */
GRANT SELECT ON dbo.Administrador TO usr_autenticacion;
GRANT SELECT ON dbo.Mesero        TO usr_autenticacion;
GRANT SELECT ON dbo.Cocina        TO usr_autenticacion;
GRANT SELECT ON dbo.Cliente       TO usr_autenticacion;

DENY INSERT, UPDATE, DELETE ON dbo.Administrador  TO usr_autenticacion;
DENY INSERT, UPDATE, DELETE ON dbo.Mesero         TO usr_autenticacion;
DENY INSERT, UPDATE, DELETE ON dbo.Cocina         TO usr_autenticacion;
DENY INSERT, UPDATE, DELETE ON dbo.Cliente        TO usr_autenticacion;
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.Mesa          TO usr_autenticacion;
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.Producto      TO usr_autenticacion;
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.Pedido        TO usr_autenticacion;
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.DetallePedido TO usr_autenticacion;
GO

/* ---- usr_administrador: acceso completo (CRUD en todas las tablas) ---- */
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Mesa           TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Producto       TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Administrador  TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Mesero         TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Cocina         TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Cliente        TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Pedido         TO usr_administrador;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.DetallePedido  TO usr_administrador;
GO

/* ---- usr_mesero ---- */
GRANT SELECT, UPDATE ON dbo.Mesa          TO usr_mesero;
GRANT SELECT         ON dbo.Producto      TO usr_mesero;
GRANT SELECT         ON dbo.Administrador TO usr_mesero;
GRANT SELECT         ON dbo.Mesero        TO usr_mesero;
GRANT SELECT         ON dbo.Cocina        TO usr_mesero;
GRANT SELECT         ON dbo.Cliente       TO usr_mesero;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Pedido        TO usr_mesero;
GRANT SELECT, INSERT, DELETE         ON dbo.DetallePedido TO usr_mesero;

DENY INSERT, DELETE         ON dbo.Mesa          TO usr_mesero;
DENY INSERT, UPDATE, DELETE ON dbo.Producto      TO usr_mesero;
DENY INSERT, UPDATE, DELETE ON dbo.Administrador TO usr_mesero;
DENY INSERT, UPDATE, DELETE ON dbo.Mesero        TO usr_mesero;
DENY INSERT, UPDATE, DELETE ON dbo.Cocina        TO usr_mesero;
DENY INSERT, UPDATE, DELETE ON dbo.Cliente       TO usr_mesero;
DENY UPDATE                 ON dbo.DetallePedido TO usr_mesero;
GO

/* ---- usr_cocina ---- */
GRANT SELECT         ON dbo.Mesa          TO usr_cocina;
GRANT SELECT         ON dbo.Producto      TO usr_cocina;
GRANT SELECT         ON dbo.Administrador TO usr_cocina;
GRANT SELECT         ON dbo.Mesero        TO usr_cocina;
GRANT SELECT         ON dbo.Cocina        TO usr_cocina;
GRANT SELECT         ON dbo.Cliente       TO usr_cocina;
GRANT SELECT, UPDATE ON dbo.Pedido        TO usr_cocina;
GRANT SELECT         ON dbo.DetallePedido TO usr_cocina;

DENY INSERT, UPDATE, DELETE ON dbo.Mesa          TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.Producto      TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.Administrador TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.Mesero        TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.Cocina        TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.Cliente       TO usr_cocina;
DENY INSERT, DELETE         ON dbo.Pedido        TO usr_cocina;
DENY INSERT, UPDATE, DELETE ON dbo.DetallePedido TO usr_cocina;
GO

/* ---- usr_cliente ---- */
GRANT SELECT         ON dbo.Mesa          TO usr_cliente;
GRANT SELECT         ON dbo.Producto      TO usr_cliente;
GRANT SELECT         ON dbo.Administrador TO usr_cliente;
GRANT SELECT         ON dbo.Mesero        TO usr_cliente;
GRANT SELECT         ON dbo.Cocina        TO usr_cliente;
GRANT SELECT, INSERT, UPDATE ON dbo.Cliente       TO usr_cliente;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Pedido        TO usr_cliente;
GRANT SELECT, INSERT, DELETE         ON dbo.DetallePedido TO usr_cliente;

DENY INSERT, UPDATE, DELETE ON dbo.Mesa          TO usr_cliente;
DENY INSERT, UPDATE, DELETE ON dbo.Producto      TO usr_cliente;
DENY INSERT, UPDATE, DELETE ON dbo.Administrador TO usr_cliente;
DENY INSERT, UPDATE, DELETE ON dbo.Mesero        TO usr_cliente;
DENY INSERT, UPDATE, DELETE ON dbo.Cocina        TO usr_cliente;
DENY DELETE                 ON dbo.Cliente       TO usr_cliente;
DENY UPDATE                 ON dbo.DetallePedido TO usr_cliente;
GO

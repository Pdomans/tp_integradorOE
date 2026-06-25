import pyodbc
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")




def conectar_bd():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        "Trusted_Connection=yes;"
    )

def buscar_usuario(idusuario):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT u.idusuario, u.nombre, s.nombresector, u.activo
        FROM usuarios u
        INNER JOIN sectores s ON u.idsector = s.idsector
        WHERE u.idusuario = ?
    """, idusuario)

    usuario = cursor.fetchone()
    conexion.close()
    return usuario


def obtener_categorias():
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT idcategoria, nombrecategoria
        FROM categorias
        ORDER BY idcategoria
    """)

    datos = cursor.fetchall()
    conexion.close()
    return datos


def obtener_impactos():
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT idimpacto, nombreimpacto
        FROM impacto
        ORDER BY idimpacto
    """)

    datos = cursor.fetchall()
    conexion.close()
    return datos


def obtener_nombre_categoria(idcategoria):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT nombrecategoria
        FROM categorias
        WHERE idcategoria = ?
    """, idcategoria)

    dato = cursor.fetchone()
    conexion.close()

    return dato.nombrecategoria if dato else "Sin categoria"


def obtener_nombre_impacto(idimpacto):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT nombreimpacto
        FROM impacto
        WHERE idimpacto = ?
    """, idimpacto)

    dato = cursor.fetchone()
    conexion.close()

    return dato.nombreimpacto if dato else "Sin impacto"


def guardar_ticket(datos):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO tickets (
            nroticket,
            legajo,
            idcategoria,
            idimpacto,
            idestado,
            descripcion,
            fechacreacion,
            fechacierre,
            observaciones
        )
        OUTPUT INSERTED.idticket
        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), NULL, NULL)
    """, (
        "TEMP",
        datos["idusuario"],
        datos["idcategoria"],
        datos["idimpacto"],
        1,
        datos["descripcion"]
    ))

    idticket = int(cursor.fetchone()[0])
    nroticket = f"TK-2026-{idticket:04d}"

    cursor.execute("""
        UPDATE tickets
        SET nroticket = ?
        WHERE idticket = ?
    """, nroticket, idticket)

    conexion.commit()
    conexion.close()

    return nroticket


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["estado"] = "esperando_legajo"

    await update.message.reply_text(
        "Hola, soy el Bot de Soporte IT.\n\nIngrese su legajo:"
    )


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    estado = context.user_data.get("estado")

    if estado == "esperando_legajo":

        if not texto.isdigit():
            await update.message.reply_text("El legajo debe ser numerico. Intente nuevamente:")
            return

        usuario = buscar_usuario(int(texto))

        if usuario is None:
            await update.message.reply_text("Legajo invalido. Intente nuevamente:")
            return

        if usuario.activo == 0:
            await update.message.reply_text("Usuario inactivo. Contacte a soporte.")
            return

        context.user_data["idusuario"] = usuario.idusuario
        context.user_data["nombre"] = usuario.nombre
        context.user_data["sector"] = usuario.nombresector
        context.user_data["estado"] = "esperando_categoria"

        categorias = obtener_categorias()

        mensaje = (
            f"Bienvenido {usuario.nombre}.\n"
            f"Sector: {usuario.nombresector}\n\n"
            "Seleccione una categoria:\n"
        )

        for c in categorias:
            mensaje += f"{c.idcategoria} - {c.nombrecategoria}\n"

        await update.message.reply_text(mensaje)
        return

    if estado == "esperando_categoria":

        if not texto.isdigit():
            await update.message.reply_text("Seleccione una categoria valida.")
            return

        categorias = obtener_categorias()
        ids_validos = [c.idcategoria for c in categorias]

        if int(texto) not in ids_validos:
            await update.message.reply_text("Categoria inexistente. Intente nuevamente.")
            return

        context.user_data["idcategoria"] = int(texto)
        context.user_data["estado"] = "esperando_descripcion"

        await update.message.reply_text("Describa brevemente el incidente:")
        return

    if estado == "esperando_descripcion":

        if len(texto) < 5:
            await update.message.reply_text("La descripcion es muy corta. Intente nuevamente:")
            return

        context.user_data["descripcion"] = texto
        context.user_data["estado"] = "esperando_impacto"

        impactos = obtener_impactos()

        mensaje = "Seleccione el impacto:\n"

        for i in impactos:
            mensaje += f"{i.idimpacto} - {i.nombreimpacto}\n"

        await update.message.reply_text(mensaje)
        return

    if estado == "esperando_impacto":

        if not texto.isdigit():
            await update.message.reply_text("Seleccione un impacto valido.")
            return

        impactos = obtener_impactos()
        ids_validos = [i.idimpacto for i in impactos]

        if int(texto) not in ids_validos:
            await update.message.reply_text("Impacto inexistente. Intente nuevamente.")
            return

        context.user_data["idimpacto"] = int(texto)
        context.user_data["estado"] = "confirmando_ticket"

        categoria = obtener_nombre_categoria(context.user_data["idcategoria"])
        impacto = obtener_nombre_impacto(context.user_data["idimpacto"])

        resumen = (
            "Resumen de la solicitud:\n\n"
            f"Usuario: {context.user_data['nombre']}\n"
            f"Sector: {context.user_data['sector']}\n"
            f"Categoria: {categoria}\n"
            f"Impacto: {impacto}\n"
            f"Descripcion: {context.user_data['descripcion']}\n\n"
            "Desea generar el ticket? Responda SI o NO."
        )

        await update.message.reply_text(resumen)
        return

    if estado == "confirmando_ticket":

        if texto.upper() == "NO":
            context.user_data.clear()
            await update.message.reply_text(
                "Solicitud cancelada.\n\nUse /start para iniciar nuevamente."
            )
            return

        if texto.upper() != "SI":
            await update.message.reply_text("Respuesta invalida. Escriba SI o NO.")
            return

        nombre = context.user_data["nombre"]
        sector = context.user_data["sector"]
        categoria = obtener_nombre_categoria(context.user_data["idcategoria"])
        impacto = obtener_nombre_impacto(context.user_data["idimpacto"])
        descripcion = context.user_data["descripcion"]

        nroticket = guardar_ticket(context.user_data)

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        context.user_data.clear()

        await update.message.reply_text(
            f"""
TICKET GENERADO CORRECTAMENTE

Numero: {nroticket}

Usuario: {nombre}

Sector: {sector}

Categoria: {categoria}

Impacto: {impacto}

Descripcion:
{descripcion}

Fecha: {fecha}

Estado: Abierto

Su solicitud fue registrada correctamente.
El area de soporte analizara el incidente a la brevedad.

Gracias por utilizar el Bot de Soporte IT.

Para generar una nueva solicitud escriba:
/start
"""
        )
        return

    await update.message.reply_text("Use /start para iniciar una nueva solicitud.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
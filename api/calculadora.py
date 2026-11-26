"""Calculadora de K2 para Vercel."""

import datetime, html
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

SERVICIOS = {
    "1": {"nombre": "Recolección a demanda", "precio": 25000},
    "2": {"nombre": "Contenedor K2 + suscripción", "precio": 120000},
    "3": {"nombre": "Certificado de aprovechamiento", "precio": 80000},
}

DESCUENTOS = {
    "K2PRIMERA": 0.20,
    "K2COLEGIOS": 0.10,
}


def formatear_pesos(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")


def calcular_pedido(servicio, cantidad, codigo=""):
    if servicio not in SERVICIOS:
        raise ValueError("Selecciona un servicio de la lista.")

    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero.")

    if cantidad < 1:
        raise ValueError("La cantidad debe ser mínimo 1.")

    precio = SERVICIOS[servicio]["precio"]
    subtotal = precio * cantidad

    codigo = codigo.strip().upper()
    porcentaje = DESCUENTOS.get(codigo, 0)

    descuento = subtotal * porcentaje
    total = subtotal - descuento

    if codigo == "":
        mensaje = "Sin código de descuento."
    elif porcentaje > 0:
        mensaje = f"Código aplicado: {int(porcentaje * 100)}% de descuento."
    else:
        mensaje = "El código no es válido, se cobra el valor normal."

    return {
        "servicio": SERVICIOS[servicio]["nombre"],
        "cantidad": cantidad,
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
        "mensaje": mensaje,
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.enviar_pagina(
            "<h2>Calculadora K2</h2>"
            "<p>Ingresa a la página para realizar tu solicitud.</p>"
            '<a href="/">Volver a K2</a>'
        )

    def do_POST(self):
        longitud = int(self.headers.get("Content-Length", 0))
        datos = self.rfile.read(longitud).decode("utf-8")
        formulario = parse_qs(datos)

        servicio = formulario.get("servicio", [""])[0]
        cantidad = formulario.get("cantidad", [""])[0]
        codigo = formulario.get("codigo", [""])[0]

        try:
            resultado = calcular_pedido(servicio, cantidad, codigo)

            contenido = f"""
            <h1>Resumen de tu solicitud K2</h1>

            <p><strong>Servicio:</strong> {html.escape(resultado["servicio"])}</p>
            <p><strong>Cantidad:</strong> {resultado["cantidad"]}</p>
            <p><strong>Subtotal:</strong> {formatear_pesos(resultado["subtotal"])}</p>
            <p><strong>Descuento:</strong> {formatear_pesos(resultado["descuento"])}</p>

            <h2>Total: {formatear_pesos(resultado["total"])}</h2>

            <p>{html.escape(resultado["mensaje"])}</p>

            <a href="/#calculadora">Volver a la calculadora</a>
            """

            self.enviar_pagina(contenido)

        except ValueError as error:
            contenido = f"""
            <h1>No se pudo calcular tu solicitud</h1>
            <p>{html.escape(str(error))}</p>
            <a href="/#calculadora">Volver a intentarlo</a>
            """

            self.enviar_pagina(contenido)

    def enviar_pagina(self, contenido):
        pagina = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resultado | K2</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f2f7f3;
                    padding: 30px;
                    color: #24352b;
                }}
                .resultado {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }}
                h1, h2 {{
                    color: #23834b;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    color: #23834b;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="resultado">
                {contenido}
            </div>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(pagina.encode("utf-8"))
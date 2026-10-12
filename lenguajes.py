"""Dibuja `img/lenguajes.svg` con los lenguajes de mis repositorios públicos.

Cada repositorio pesa lo mismo: se promedia el porcentaje de cada lenguaje
entre todos, para que uno muy grande no tape a los demás. No cuenta los forks.
"""

import json
import os
import urllib.request
from collections import Counter

USUARIO = "safloresmo"
MOSTRAR = 5
ANCHO_LETRA = 7.3

# Colores que usa GitHub para cada lenguaje.
COLORES = {
    "C": "#555555", "C++": "#f34b7d", "Python": "#3572A5", "QML": "#44a51c", "VHDL": "#adb2cb",
    "Rust": "#dea584", "Vue": "#41b883", "Shell": "#89e051", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "Tcl": "#e4cc98", "HTML": "#e34c26", "CSS": "#663399",
}
OTROS = "#8b949e"


def pedir(ruta):
    cabeceras = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        cabeceras["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(f"https://api.github.com{ruta}", headers=cabeceras)) as r:
        return json.load(r)


def porcentajes():
    repos = [r["name"] for r in pedir(f"/users/{USUARIO}/repos?per_page=100&type=owner") if not r["fork"]]
    total, contados = Counter(), 0
    for repo in repos:
        lenguajes = pedir(f"/repos/{USUARIO}/{repo}/languages")
        suma = sum(lenguajes.values())
        if not suma:
            continue
        contados += 1
        for lenguaje, tamano in lenguajes.items():
            total[lenguaje] += tamano / suma
    partes = [(nombre, valor / contados) for nombre, valor in total.most_common(MOSTRAR)]
    resto = 1 - sum(valor for _, valor in partes)
    if resto > 0.005:
        partes.append(("Otros", resto))
    return partes


def dibujar(partes):
    etiquetas = [f"{nombre} {round(valor * 100)}%" for nombre, valor in partes]
    ancho = round(sum(10 + len(e) * ANCHO_LETRA + 22 for e in etiquetas) - 16)

    barra, leyenda, x_barra, x = [], [], 0.0, 6.0
    for (nombre, valor), etiqueta in zip(partes, etiquetas):
        color = COLORES.get(nombre, OTROS)
        barra.append(f'<rect x="{x_barra:.1f}" width="{valor * ancho:.1f}" height="8" fill="{color}"/>')
        x_barra += valor * ancho
        leyenda.append(f'<circle cx="{x:.1f}" cy="27" r="5" fill="{color}"/><text x="{x + 10:.1f}" y="31.5">{etiqueta}</text>')
        x += 10 + len(etiqueta) * ANCHO_LETRA + 22

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="38" viewBox="0 0 {ancho} 38" role="img" '
        f'aria-label="{", ".join(etiquetas)}">'
        f'<clipPath id="barra"><rect width="{ancho}" height="8" rx="4"/></clipPath>'
        f'<g clip-path="url(#barra)">{"".join(barra)}</g>'
        "<g font-family=\"-apple-system, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif\" "
        f'font-size="13" fill="#8b949e">{"".join(leyenda)}</g></svg>\n'
    )


if __name__ == "__main__":
    with open("img/lenguajes.svg", "w") as archivo:
        archivo.write(dibujar(porcentajes()))

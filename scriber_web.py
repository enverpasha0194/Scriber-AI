import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            width: 100vw;
            height: 100vh;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, Helvetica, sans-serif;
        }

        .container {
            text-align: center;
        }

        img {
            width: 180px;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 36px;
            letter-spacing: 2px;
            margin-bottom: 15px;
        }

        p {
            font-size: 15px;
            color: #555;
            max-width: 420px;
            margin: auto;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://media.tenor.com/K5wSW-CGK9wAAAAi/maintenance-under-maintenance.gif">
        <h1>UYGULAMA ÇALIŞMA ALTINDA!</h1>
        <p>
            Tekrardan Açılıyoruz!<br>
            Performans artışı, stabilite ve birkaç gizli dokunuş yapılıyor.<br><br>
            Birazdan buradayız. Kahveni al gel ☕
        </p>
    </div>
</body>
</html>
"""

components.html(html_code, height=600)

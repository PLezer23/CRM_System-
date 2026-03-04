import os
import sqlite3
import sys
import pymorphy3 as pymorphy2
from bot import show_db
from flask import Flask, render_template_string, request

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from database.connection import Database
app = Flask(__name__)

morph = pymorphy2.MorphAnalyzer()
db = Database()
DB_FILE_PATH = os.path.join(project_root, 'bot', 'KOKC.db')

conn = sqlite3.connect(DB_FILE_PATH)

SEARCH_CONFIG = {
    "clients": ["first_name", "user_id"],
    "manager_requests": ["user_id", "created_at"],
    "messages": ["user_id", "message", "response", "created_at"]
}

TABLE_GROUPS = {
    'clients': {
        'title': 'Клиенты',
        'tables': ['clients']
    },
    'manager_requests': {   
        'title': 'Запросы менеджера',
        'tables': ['manager_requests']
    },
    'messages': {
        'title': 'Сообщения',
        'tables': ['messages']
    },
    'message_links': {
        'title': 'Ссылки на сообщения',
        'tables': []
    }
}


def filter_table_data(all_data, search_query):
    if not search_query:
        return all_data

    search_query = search_query.lower().strip()
    filtered_data = {}

    for table_name, table_data in all_data.items():
        if table_name == "error":
            filtered_data[table_name] = table_data
            continue

        filtered_rows = []

        for row in table_data.get("rows", []):
            for value in row.values():
                if value is not None and search_query in str(value).lower():
                    filtered_rows.append(row)
                    break

        filtered_data[table_name] = {
            "columns": table_data.get("columns", []),
            "rows": filtered_rows
        }

    return filtered_data


def group_tables(all_data):
    if "error" in all_data:
        return all_data

    grouped_data = {
        'clients': {'title': 'Клиенты', 'data': {}},
        'manager_requests': {'title': 'Запросы менеджера', 'data': {}},
        'messages': {'title': 'Сообщения', 'data': {}},
        'message_links': {'title': 'Прочее', 'data': {}}
    }

    for table_name, table_info in all_data.items():
        if table_name == 'clients':
            grouped_data['clients']['data'][table_name] = table_info
        elif table_name == 'manager_requests':
            grouped_data['manager_requests']['data'][table_name] = table_info
        elif table_name == 'messages':
            grouped_data['messages']['data'][table_name] = table_info
        else:
            grouped_data['message_links']['data'][table_name] = table_info

    return grouped_data


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body { background-color: #f8f9fa; }
        .side-menu {
            background-color: #343a40;
            min-height: 100vh;
            padding: 0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }
        .side-menu .menu-item {
            padding: 12px 20px;
            color: #adb5bd;
            cursor: pointer;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        .side-menu .menu-item:hover {
            background-color: #495057;
            color: white;
        }
        .side-menu .menu-item.active {
            background-color: #0d6efd;
            color: white;
            border-left-color: #ffc107;
        }
        .side-menu .badge {
            float: right;
            background-color: #6c757d;
        }
        .content-area {
            padding: 20px;
            max-height: 100vh;
            overflow-y: auto;
        }
        .card-header {
            font-weight: bold;
            background-color: #e9ecef;
        }
        .dashboard-card {
            border: none;
            border-radius: 15px;
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
            overflow: hidden;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .dashboard-card .card-body {
            padding: 1.5rem;
        }
        .text-white-50 {
            color: rgba(255,255,255,0.7) !important;
        }
        .icon-wrapper {
            opacity: 0.8;
        }
        .search-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 10px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .search-box {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-grow: 1;
        }
        .search-input {
            border-radius: 30px;
            border: 1px solid #dee2e6;
            padding: 10px 20px;
            width: 100%;
            max-width: 500px;
            font-size: 1rem;
        }
        .search-input:focus {
            outline: none;
            border-color: #0d6efd;
            box-shadow: 0 0 0 3px rgba(13,110,253,0.25);
        }
        .stats-badge {
            background: #e9ecef;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-2 p-0 side-menu">
            <div style="padding: 20px; border-bottom: 1px solid #495057;">
                <h6 class="mb-0 text-white">КОКЦ CRM</h6>
                <small class="text-secondary">Панель управления</small>
            </div>

            <div class="menu-item" onclick="showDashboard()">
                <i class="bi bi-speedometer2 me-2"></i>Dashboard
            </div>

            {% for group_id, group_info in grouped_data.items() %}
            <div class="menu-item {% if loop.first %}active{% endif %}" 
                 onclick="showTable('{{ group_id }}')">
                <i class="bi 
                    {% if group_id == 'clients' %}bi-people
                    {% elif group_id == 'messages' %}bi-chat-dots
                    {% elif group_id == 'manager_requests' %}bi-envelope
                    {% else %}bi-table{% endif %} me-2"></i>
                {{ group_info.title }}
                <span class="badge">{{ group_info.data.keys()|length }}</span>
            </div>
            {% endfor %}
        </div>

        <div class="col-md-10 content-area">

            <div class="search-container">
                <form method="GET" action="/" class="search-box">
                    <i class="bi bi-search text-secondary"></i>
                    <input type="text" class="search-input" name="search" 
                           placeholder="Поиск по ID, имени, сообщениям..."
                           value="{{ search_query or '' }}">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-search"></i> Найти
                    </button>
                    {% if search_query %}
                    <a href="/" class="btn btn-outline-secondary">
                        <i class="bi bi-x-circle"></i> Сбросить
                    </a>
                    {% endif %}
                </form>
            </div>

            <div id="dashboard" class="table-container" style="display: none;">
                <div class="row g-4">
                    <div class="col-md-6 col-lg-3">
                        <div class="card dashboard-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="badge bg-white text-dark mb-2">Клиенты</span>
                                        <h2 class="text-white mb-0">{{ grouped_data.clients.data.clients.rows|length if grouped_data.clients and grouped_data.clients.data.clients else 0 }}</h2>
                                        <small class="text-white-50">всего в системе</small>
                                    </div>
                                    <div class="icon-wrapper">
                                        <i class="bi bi-people-fill" style="font-size: 3rem; color: rgba(255,255,255,0.3);"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card dashboard-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="badge bg-white text-dark mb-2">Сообщения</span>
                                        <h2 class="text-white mb-0">{{ grouped_data.messages.data.messages.rows|length if grouped_data.messages and grouped_data.messages.data.messages else 0 }}</h2>
                                        <small class="text-white-50">всего диалогов</small>
                                    </div>
                                    <div class="icon-wrapper">
                                        <i class="bi bi-chat-dots-fill" style="font-size: 3rem; color: rgba(255,255,255,0.3);"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card dashboard-card" style="background: linear-gradient(135deg, #5fa8f4 0%, #2b3c5e 100%);">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="badge bg-white text-dark mb-2">Запросы</span>
                                        <h2 class="text-white mb-0">{{ grouped_data.manager_requests.data.manager_requests.rows|length if grouped_data.manager_requests and grouped_data.manager_requests.data.manager_requests else 0 }}</h2>
                                        <small class="text-white-50">всего запросов</small>
                                    </div>
                                    <div class="icon-wrapper">
                                        <i class="bi bi-envelope-fill" style="font-size: 3rem; color: rgba(255,255,255,0.3);"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6 col-lg-3">
                        <div class="card dashboard-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="badge bg-white text-dark mb-2">Таблицы</span>
                                        <h2 class="text-white mb-0">{{ grouped_data.keys()|length }}</h2>
                                        <small class="text-white-50">всего групп</small>
                                    </div>
                                    <div class="icon-wrapper">
                                        <i class="bi bi-table" style="font-size: 3rem; color: rgba(255,255,255,0.3);"></i>
                                    </div>
                                </div>
                                <div class="mt-3 text-white-50 small">
                                    <i class="bi bi-database"></i> SQLite
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {% for group_id, group_info in grouped_data.items() %}
            <div id="table-{{ group_id }}" class="table-container" 
                 style="display: {% if loop.first %}block{% else %}none{% endif %};">
                <h4 class="mb-3">{{ group_info.title }}</h4>

                {% for table_name, info in group_info.data.items() %}
                <div class="card shadow-sm mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><i class="bi bi-table me-2"></i>{{ table_name }}</span>
                        <span class="badge bg-primary rounded-pill">Записей: {{ info.rows|length }}</span>
                    </div>
                    <div class="card-body p-0">
                        {% if info.rows %}
                        <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                            <table class="table table-hover table-striped mb-0">
                                <thead class="table-light" style="position: sticky; top: 0; background: #f8f9fa;">
                                    <tr>
                                        {% for col in info.columns %}
                                        <th>{{ col }}</th>
                                        {% endfor %}
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for row in info.rows %}
                                    <tr>
                                        {% for col in info.columns %}
                                        <td>
                                            {% if col == 'created_at' or col == 'timestamp' or col == 'date' %}
                                                {{ row[col] }}
                                            {% elif col == 'user_id' or col == 'id' %}
                                                <span class="badge bg-secondary">{{ row[col] }}</span>
                                            {% elif row[col] is not none and row[col] is string and row[col]|length > 100 %}
                                                {{ row[col][:100] }}...
                                            {% else %}
                                                {{ row[col] }}
                                            {% endif %}
                                        </td>
                                        {% endfor %}
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="p-4 text-center text-muted">
                            <i class="bi bi-database-slash" style="font-size: 2rem;"></i>
                            <p class="mt-2">Нет данных</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<script>
function showTable(groupId) {
    document.querySelectorAll('[id^="table-"], #dashboard').forEach(el => {
        el.style.display = 'none';
    });
    document.getElementById('table-' + groupId).style.display = 'block';
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

function showDashboard() {
    document.querySelectorAll('[id^="table-"], #dashboard').forEach(el => {
        el.style.display = 'none';
    });
    document.getElementById('dashboard').style.display = 'block';
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search') or request.form.get('search', '')
    all_data = show_db.get_tables_info(DB_FILE_PATH)
    if search_query:
        all_data = filter_table_data(all_data, search_query)
    if "error" in all_data:
        return f'<div class="alert alert-danger m-5"><strong>Ошибка:</strong> {all_data["error"]}</div>'
    grouped_data = group_tables(all_data)
    return render_template_string(HTML_TEMPLATE, grouped_data=grouped_data, search_query=search_query)


app.run(debug=True, host='0.0.0.0', port=5000)

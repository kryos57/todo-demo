"""
シンプルTodoアプリ (Claude Code デモ用)

Python標準ライブラリ (tkinter) のみで動作します。
追加インストール不要。Windowsで以下のコマンドだけで起動できます。

    python todo_app.py

タスクは同じフォルダの tasks.json に自動保存されます。
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


# タスクを保存するファイル (このスクリプトと同じ場所に作られます)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

# 配色 (落ち着いたティール基調)
COLOR_BG = "#0f2a2e"        # 背景 (濃いティール)
COLOR_PANEL = "#12383d"     # パネル
COLOR_ACCENT = "#028090"    # アクセント
COLOR_ACCENT_LIGHT = "#5eead4"  # 明るいアクセント
COLOR_TEXT = "#f4f8f8"      # 文字
COLOR_DONE = "#6b7c7e"      # 完了タスクの文字

# タスクに指定できるカテゴリ
CATEGORIES = ["仕事", "家事", "買い物", "私用", "その他"]
DEFAULT_CATEGORY = "その他"

# カテゴリごとのタグ色
CATEGORY_COLORS = {
    "仕事": "#ef6f6c",
    "家事": "#f4a261",
    "買い物": "#e9c46a",
    "私用": "#5eead4",
    "その他": "#9aa5a8",
}


class TaskStore:
    """タスクの読み書きを担当するクラス。

    タスクは辞書のリストで持ちます。
        {"title": "牛乳を買う", "done": False, "category": "買い物"}
    """

    def __init__(self, path):
        self.path = path
        self.tasks = []
        self.load()

    def load(self):
        """ファイルからタスクを読み込む。無ければ空リスト。"""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
            # カテゴリ未設定の既存タスクにはデフォルトを補う
            for task in self.tasks:
                task.setdefault("category", DEFAULT_CATEGORY)

    def save(self):
        """現在のタスクをファイルに書き出す。"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add(self, title, category=DEFAULT_CATEGORY):
        """新しいタスクを追加する。"""
        self.tasks.append({"title": title, "done": False, "category": category})
        self.save()

    def toggle(self, index):
        """完了 / 未完了 を切り替える。"""
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save()

    def delete(self, index):
        """タスクを削除する。"""
        del self.tasks[index]
        self.save()

    def count_remaining(self):
        """未完了タスクの件数を返す。"""
        remaining = 0
        for task in self.tasks:
            if not task["done"]:
                remaining = remaining + 1
        return remaining


class TodoApp:
    """画面とユーザー操作を担当するクラス。"""

    def __init__(self, root):
        self.root = root
        self.store = TaskStore(DATA_FILE)

        self.root.title("Todo")
        self.root.geometry("440x560")
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(380, 460)

        self._build_header()
        self._build_input()
        self._build_list()
        self._build_footer()

        self.refresh()

    # ---- 画面づくり ----

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLOR_BG)
        header.pack(fill="x", padx=24, pady=(24, 8))

        title = tk.Label(
            header, text="今日のタスク", bg=COLOR_BG, fg=COLOR_TEXT,
            font=("Yu Gothic UI", 20, "bold"),
        )
        title.pack(anchor="w")

    def _build_input(self):
        box = tk.Frame(self.root, bg=COLOR_BG)
        box.pack(fill="x", padx=24, pady=8)

        self.entry = tk.Entry(
            box, font=("Yu Gothic UI", 12), bg=COLOR_PANEL, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT, relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        # Enterキーでも追加できるようにする
        self.entry.bind("<Return>", lambda event: self.on_add())

        add_btn = tk.Button(
            box, text="追加", command=self.on_add, bg=COLOR_ACCENT, fg=COLOR_TEXT,
            font=("Yu Gothic UI", 11, "bold"), relief="flat",
            activebackground=COLOR_ACCENT_LIGHT, cursor="hand2", padx=16,
        )
        add_btn.pack(side="right", ipady=4)

        category_box = tk.Frame(self.root, bg=COLOR_BG)
        category_box.pack(fill="x", padx=24, pady=(0, 8))

        tk.Label(
            category_box, text="カテゴリ", bg=COLOR_BG, fg=COLOR_DONE,
            font=("Yu Gothic UI", 10),
        ).pack(side="left", padx=(0, 8))

        self.category_var = tk.StringVar(value=DEFAULT_CATEGORY)
        self.category_combo = ttk.Combobox(
            category_box, textvariable=self.category_var, values=CATEGORIES,
            state="readonly", font=("Yu Gothic UI", 10), width=10,
        )
        self.category_combo.pack(side="left")

    def _build_list(self):
        # スクロールできるタスク一覧
        container = tk.Frame(self.root, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=8)

        self.list_frame = tk.Frame(container, bg=COLOR_BG)
        self.list_frame.pack(fill="both", expand=True)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=COLOR_BG)
        footer.pack(fill="x", padx=24, pady=(8, 24))

        self.status = tk.Label(
            footer, text="", bg=COLOR_BG, fg=COLOR_DONE,
            font=("Yu Gothic UI", 10),
        )
        self.status.pack(side="left")

    # ---- 操作 ----

    def on_add(self):
        """入力欄のテキストをタスクとして追加する。"""
        title = self.entry.get().strip()
        if title == "":
            return
        category = self.category_var.get() or DEFAULT_CATEGORY
        self.store.add(title, category)
        self.entry.delete(0, tk.END)
        self.refresh()

    def on_toggle(self, index):
        self.store.toggle(index)
        self.refresh()

    def on_delete(self, index):
        self.store.delete(index)
        self.refresh()

    def refresh(self):
        """タスク一覧を画面に描き直す。"""
        # いったん全部消してから作り直す
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for index, task in enumerate(self.store.tasks):
            row = tk.Frame(self.list_frame, bg=COLOR_PANEL)
            row.pack(fill="x", pady=4)

            # チェックボックス代わりのボタン
            mark = "✓" if task["done"] else "○"
            check = tk.Button(
                row, text=mark, width=3, relief="flat", cursor="hand2",
                bg=COLOR_PANEL, fg=COLOR_ACCENT_LIGHT,
                font=("Yu Gothic UI", 12, "bold"),
                activebackground=COLOR_PANEL,
                command=lambda i=index: self.on_toggle(i),
            )
            check.pack(side="left", padx=(8, 4), pady=8)

            # カテゴリタグ
            category = task.get("category", DEFAULT_CATEGORY)
            tag_color = COLOR_DONE if task["done"] else CATEGORY_COLORS.get(category, COLOR_DONE)
            tag = tk.Label(
                row, text=category, bg=COLOR_PANEL, fg=tag_color,
                font=("Yu Gothic UI", 9, "bold"),
            )
            tag.pack(side="left", padx=(0, 4), pady=8)

            # タスク名 (完了なら色を薄く)
            color = COLOR_DONE if task["done"] else COLOR_TEXT
            label = tk.Label(
                row, text=task["title"], bg=COLOR_PANEL, fg=color,
                font=("Yu Gothic UI", 12), anchor="w",
            )
            label.pack(side="left", fill="x", expand=True, pady=8)

            # 削除ボタン
            delete = tk.Button(
                row, text="削除", relief="flat", cursor="hand2",
                bg=COLOR_PANEL, fg=COLOR_DONE,
                font=("Yu Gothic UI", 10),
                activebackground=COLOR_PANEL,
                command=lambda i=index: self.on_delete(i),
            )
            delete.pack(side="right", padx=8)

        # 残り件数を更新
        remaining = self.store.count_remaining()
        self.status.config(text="残り " + str(remaining) + " 件")


def main():
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

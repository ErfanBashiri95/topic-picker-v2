import os
import json
import csv
import io

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    Response,
)

# تلاش برای ایمپورت supabase؛ اگر نبود، برنامه لوکال با JSON کار می‌کند
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

app = Flask(__name__)
app.secret_key = "change-this-to-a-strong-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
TOPICS_FILE = os.path.join(DATA_DIR, "topics.json")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "022025"

# ---------------- Supabase Config ----------------

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if create_client and SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    USE_SUPABASE = True
else:
    supabase = None
    USE_SUPABASE = False



# ---------------- Helper functions ----------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_users():
    return load_json(USERS_FILE)


def get_topics():
    """
    اگر Supabase تنظیم شده باشد، از جدول topics می‌خوانیم.
    در غیر این صورت از فایل topics.json قبلی.
    """
    if USE_SUPABASE and supabase:
        res = supabase.table("topics").select("*").order("id").execute()
        return res.data or []
    else:
        return load_json(TOPICS_FILE)


def set_topics(topics):
    """
    اگر Supabase فعال است، فقط فیلد chosen_by را بر اساس id آپدیت می‌کنیم.
    در غیر این صورت، در فایل topics.json ذخیره می‌کنیم.
    """
    if USE_SUPABASE and supabase:
        for t in topics:
            supabase.table("topics").update(
                {"chosen_by": t.get("chosen_by")}
            ).eq("id", t["id"]).execute()
    else:
        save_json(TOPICS_FILE, topics)


# ---------------- Routes ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session and not session.get("is_admin"):
        return redirect(url_for("topics_page"))
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        # اگر ادمین اینجا یوزرنیم زد، بفرستش به لاگین ادمین
        if username == ADMIN_USERNAME:
            return redirect(url_for("admin_login"))

        users = get_users()
        for u in users:
            if u["username"] == username:
                session["user"] = username
                session["is_admin"] = False
                return redirect(url_for("topics_page"))

        error = "یوزرنیم معتبر نیست."
    return render_template("login.html", error=error)


@app.route("/topics", methods=["GET", "POST"])
def topics_page():
    if "user" not in session or session.get("is_admin"):
        return redirect(url_for("login"))

    username = session["user"]
    users = get_users()
    user_obj = next((u for u in users if u["username"] == username), None)
    display_name = user_obj["name"] if user_obj else username

    topics = get_topics()
    error = None
    success = None

    if request.method == "POST":
        selected_ids = request.form.getlist("topics")
        try:
            selected_ids = [int(x) for x in selected_ids]
        except ValueError:
            selected_ids = []

        # محدودیت حداقل/حداکثر
        if len(selected_ids) < 1:
            error = "حداقل یک سرفصل باید انتخاب کنید."
        elif len(selected_ids) > 2:
            error = "حداکثر می‌توانید دو سرفصل انتخاب کنید."
        else:
            # آخرین وضعیت topics را بخوانیم
            topics = get_topics()

            # آزاد کردن انتخاب‌های قبلی این کاربر که دیگر انتخاب نشده‌اند
            for t in topics:
                if t.get("chosen_by") == username and t["id"] not in selected_ids:
                    t["chosen_by"] = None

            conflict = False

            # ثبت انتخاب‌های جدید
            for tid in selected_ids:
                topic = next((t for t in topics if t["id"] == tid), None)
                if not topic:
                    continue

                # اگر توسط شخص دیگری گرفته شده
                if topic.get("chosen_by") not in (None, username):
                    conflict = True
                    continue

                topic["chosen_by"] = username

            set_topics(topics)

            if conflict:
                error = "برخی سرفصل‌ها قبلاً توسط دیگران گرفته شده‌اند. لطفاً لیست را دوباره بررسی کنید."
            else:
                success = "انتخاب‌های شما با موفقیت ذخیره شد."

    # برای نمایش نهایی
    topics = get_topics()
    return render_template(
        "topics.html",
        topics=topics,
        username=username,
        display_name=display_name,
        error=error,
        success=success,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- Admin ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "یوزرنیم یا پسورد ادمین اشتباه است."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    topics = get_topics()
    users = get_users()

    # بر اساس کاربر
    by_user = []
    for u in users:
        chosen = [t["title"] for t in topics if t.get("chosen_by") == u["username"]]
        by_user.append({
            "name": u["name"],
            "topics": " / ".join(chosen) if chosen else ""
        })

    return render_template(
        "admin_dashboard.html",
        by_user=by_user,
        topics=topics
    )


@app.route("/admin/reset-all", methods=["POST"])
def admin_reset_all():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    topics = get_topics()

    for t in topics:
        t["chosen_by"] = None

    set_topics(topics)

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/export.csv")
def admin_export_csv():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    topics = get_topics()
    users = get_users()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["نام", "سرفصل‌های انتخاب‌شده"])

    for u in users:
        chosen = [t["title"] for t in topics if t.get("chosen_by") == u["username"]]
        writer.writerow([u["name"], " / ".join(chosen)])

    resp = Response(
        output.getvalue().encode("utf-8-sig"),
        mimetype="text/csv; charset=utf-8",
    )
    resp.headers["Content-Disposition"] = "attachment; filename=selections.csv"
    return resp


if __name__ == "__main__":
    app.run(debug=True)

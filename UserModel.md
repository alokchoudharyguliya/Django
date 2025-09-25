Awesome—here’s a practical, end-to-end guide to Django auth that you can actually drop into real projects. It covers:

* Built-in user model (default)
* Custom user models (recommended patterns)
* Sessions & cookies
* Permissions & groups
* Login/Logout & password management
* Social auth (django-allauth & python-social-auth)
* Role-Based Access Control (RBAC) patterns

I’ll show minimal, working snippets and the “gotchas” you’ll want to avoid.

---

# 1) Built-in User Model (the default)

## Enable core auth apps

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
]
MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
]
```

## Quick usage

```python
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

user = User.objects.create_user(username="alice", email="a@b.com", password="p@ssw0rd")
user.is_staff  # admin access flag
user.is_superuser  # full access flag

u = authenticate(request, username="alice", password="p@ssw0rd")
if u is not None:
    login(request, u)
```

**When to keep the default**: small apps, prototypes, admin-only tools.
**When to avoid**: if you *might* add fields like phone, account type, or swap username for email later—start with a custom user now (easier than migrating later).

---

# 2) Custom User Models (do this early)

You have two options:

* **AbstractUser** (recommended): keeps username + everything; add your fields.
* **AbstractBaseUser**: fully custom (email as USERNAME_FIELD, etc.). More work.

## A) Extending with `AbstractUser`

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # add your fields
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
```

```python
# settings.py
AUTH_USER_MODEL = 'accounts.User'
```

**Important**: set `AUTH_USER_MODEL` **before the first migrate**. Changing it later requires a data migration and is painful.

## B) Full custom with `AbstractBaseUser`

```python
# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # prompted by createsuperuser
```

Admin registration:

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email','is_staff','is_superuser')
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email','password1','password2')}),
    )
```

---

# 3) Sessions & Cookies

Django uses server-side sessions with a session cookie (`sessionid`) by default.

```python
# settings.py
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_AGE = 1209600  # 2 weeks (seconds)
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_HTTPONLY = False  # default; token is read by forms, not JS
CSRF_COOKIE_SECURE = True     # set True in production (HTTPS)
SESSION_COOKIE_SECURE = True  # set True in production (HTTPS)
SESSION_COOKIE_SAMESITE = "Lax"  # 'Lax' or 'Strict'; choose 'None' if cross-site is required (with Secure=True)
```

**Reading/Writing session:**

```python
def view(request):
    request.session['cart_id'] = 123
    cart_id = request.session.get('cart_id')
    del request.session['cart_id']
```

**Remember Me** pattern:

* If user checks “Remember me”, set `request.session.set_expiry(1209600)`.
* Otherwise `request.session.set_expiry(0)` (expires on browser close).

---

# 4) Permissions & Groups

* **Permissions**: `add`, `change`, `delete`, `view` model perms auto-created. You can add custom.
* **Groups**: named bundles of permissions; attach users to groups.

```python
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from myapp.models import Order

# Create a custom permission
ct = ContentType.objects.get_for_model(Order)
perm = Permission.objects.create(
    codename="approve_order",
    name="Can approve order",
    content_type=ct,
)

# Create a group and add permissions
managers = Group.objects.create(name="Managers")
managers.permissions.add(perm)

# Add user to group
user.groups.add(managers)

# Check in code
user.has_perm('myapp.approve_order')      # True/False
user.has_perms(['myapp.view_order','myapp.approve_order'])
user.has_module_perms('myapp')
```

**Decorators & Mixins**

```python
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

@login_required
def dashboard(request): ...

@permission_required('myapp.approve_order')
def approve(request): ...

class ReportsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'myapp.view_report'
```

---

# 5) Login, Logout & Password Management

## URLs (built-in auth views)

```python
# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/',  auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='auth/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/password_change_done.html'), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
]
```

## Settings for password reset email

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # dev only
# In prod: use SMTP or a provider
DEFAULT_FROM_EMAIL = 'noreply@example.com'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # strongest
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':9}},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

## Template notes (example login form)

```html
<!-- templates/auth/login.html -->
<form method="post" action="{% url 'login' %}">
  {% csrf_token %}
  {{ form.non_field_errors }}
  <label>Username</label> {{ form.username }}
  <label>Password</label> {{ form.password }}
  <button type="submit">Log in</button>
</form>
```

## Programmatic login/logout

```python
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        u = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if u:
            login(request, u)  # sets the session
            return redirect('dashboard')
    # ...

def logout_view(request):
    logout(request)  # clears the session
    return redirect('login')
```

---

# 6) Social Authentication

## Option A: **django-allauth** (batteries included; recommended for email flows)

### Install & configure

```bash
pip install django-allauth
```

```python
# settings.py
INSTALLED_APPS += [
    'django.contrib.sites',   # required
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',   # add providers you need
    'allauth.socialaccount.providers.github',
]
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

LOGIN_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = 'login'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # or 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # 'mandatory' in prod if you want
```

```python
# urls.py
from django.urls import path, include
urlpatterns = [
    path('accounts/', include('allauth.urls')),
]
```

### Provider setup

* In the Django admin, go to **Sites** → ensure domain matches your dev/prod.
* **Social applications** → Add Google/GitHub with client ID & secret, assign to your Site.

### Templates

Allauth provides endpoints: `/accounts/login/`, `/accounts/signup/`, etc. You can override templates under `templates/account/` and `templates/socialaccount/`.

**Pros**: registration, email confirmation, password flows, social providers, adaptable.
**Cons**: template set is opinionated; learn its settings.

---

## Option B: **python-social-auth** (`social-auth-app-django`)

Lightweight for social only.

```bash
pip install social-auth-app-django
```

```python
# settings.py
INSTALLED_APPS += ['social_django']

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '...'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '...'
SOCIAL_AUTH_GITHUB_KEY = '...'
SOCIAL_AUTH_GITHUB_SECRET = '...'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
```

```python
# urls.py
from django.urls import path, include
urlpatterns = [
    path('oauth/', include('social_django.urls', namespace='social')),
]
```

**Pros**: simple. **Cons**: you’ll build signup/email flows yourself.

---

# 7) Role-Based Access Control (RBAC)

## Strategy 1: **Groups as roles** (fits most apps)

Define roles as groups (e.g., `Admin`, `Manager`, `Customer`) and assign permissions. Then gate views by permissions or group membership.

```python
# management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        manager, _ = Group.objects.get_or_create(name='Manager')
        perms = Permission.objects.filter(codename__in=[
            'view_order', 'change_order', 'approve_order'
        ])
        manager.permissions.set(perms)
        self.stdout.write(self.style.SUCCESS("Seeded roles"))
```

Check membership:

```python
def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Manager').exists()

from django.contrib.auth.decorators import user_passes_test
@user_passes_test(is_manager)
def manager_dashboard(request): ...
```

Or use `PermissionRequiredMixin` and check a specific permission granted by the role.

## Strategy 2: **Field on user** + custom checks

Good when roles are few and static.

```python
# accounts/models.py
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        CUSTOMER = 'CUSTOMER', 'Customer'
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
```

```python
from django.core.exceptions import PermissionDenied

def role_required(*allowed):
    def decorator(view):
        def _wrapped(request, *a, **kw):
            if not request.user.is_authenticated or request.user.role not in allowed:
                raise PermissionDenied
            return view(request, *a, **kw)
        return _wrapped
    return decorator

@role_required('ADMIN','MANAGER')
def approve_order(request, id): ...
```

**Tradeoffs**: groups are more flexible and integrate with Django admin & permissions. A role field is simpler but less granular.

## Object-level permissions (advanced)

* Use **django-guardian** for per-object permissions:

  * `assign_perm('change_project', user, project)`
  * Check with `user.has_perm('change_project', project)`

---

# 8) Common Patterns & Best Practices

* **Start with a custom user early** (AbstractUser). Even if you only add an `account_type` field, it saves future migration pain.
* **Always use `AUTH_USER_MODEL`** in foreign keys:

  ```python
  from django.conf import settings
  class Order(models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  ```
* **Email as username**: If using AbstractBaseUser, set `USERNAME_FIELD='email'`, `email` unique, custom manager, and admin integration.
* **Security**:

  * Force HTTPS; set `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`.
  * Use **Argon2** or PBKDF2 (default) for passwords.
  * Enable password validators.
  * CSRF on all POST forms.
* **Remember Me**: toggle `set_expiry` based on a checkbox.
* **Rate limit logins** (nginx/ingress level or use django-axes).
* **Signals**: send welcome emails, profile creation on `post_save` of user.
* **Admin**: hide super-danger fields with custom `ModelAdmin.fieldsets`.
* **APIs (DRF)**: use `SessionAuthentication` for web, `TokenAuthentication`/`JWT` for APIs (e.g., djangorestframework-simplejwt). Combine with `IsAuthenticated`, `DjangoModelPermissions`, or custom `permissions.BasePermission`.

---

# 9) Minimal Working Example (AbstractUser + Groups + Login)

**models.py**

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    department = models.CharField(max_length=120, blank=True)
```

**settings.py**

```python
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
```

**urls.py**

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/',  auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

**views.py**

```python
# core/views.py
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@permission_required('orders.approve_order')
def approve(request): ...
```

**seeding roles**

```python
# python manage.py shell
from django.contrib.auth.models import Group, Permission
m, _ = Group.objects.get_or_create(name='Manager')
m.permissions.set(Permission.objects.filter(codename__in=['view_order','change_order','approve_order']))
```

Assign a user:

```python
user.groups.add(m)
```

---

# 10) Troubleshooting & Gotchas

* **Swapping user late**: If you already migrated with default `auth.User`, switching to a custom user requires a *project-wide* data migration. Avoid by choosing custom at project start.
* **Circular imports**: Use `settings.AUTH_USER_MODEL` in FKs, not direct import.
* **Allauth “site mismatch”**: Ensure **Sites** domain matches your host.
* **OAuth redirect URIs** must exactly match (including scheme/port).
* **Session not persisting?** Check `SESSION_COOKIE_DOMAIN`, `SameSite`, HTTPS, and that `AuthenticationMiddleware` is enabled.
* **Forbidden (CSRF)**: Include `{% csrf_token %}` in forms; for APIs use CSRF exempt or proper headers.

---

If you tell me your project’s exact needs (email login? admin vs. vendor roles? API + SPA?), I can tailor the snippets (e.g., choose AbstractBaseUser, wire up allauth with email-first signup, seed role permissions, and add an example React/Next.js login flow against Django).



Perfect—let’s break down **“Sessions & Cookies” in Django** in a very **comprehensive, step-by-step way**. I’ll explain *what things are, how they work internally, and what settings actually do*.

---

# 🔑 What are Sessions?

* A **session** is a way Django stores per-user information **between requests**.
* HTTP is stateless → every request is independent, the server doesn’t “remember” users. Sessions solve this by linking requests from the same user.
* In Django, sessions are **server-side**: data lives in the DB (or cache/file/etc.), not in the browser.

👉 Example: Shopping cart, login state, last visited page.

---

# 🍪 What are Cookies?

* A **cookie** is a small piece of data stored in the browser.
* Django uses a cookie (`sessionid` by default) to **store the session key**.
* That key maps to the session data stored on the server.
* So:

  * **Browser cookie** → just a random session ID
  * **Server session** → actual user data

👉 This design is secure because the browser never sees your private session data.

---

# ⚙️ How Django Sessions Work Internally

1. **User sends a request** with cookies.

   * If no cookie → Django generates a new empty session.
   * If cookie has a `sessionid` → Django looks it up in the session storage.

2. **You read/write data** via `request.session`.

   * Example: `request.session["cart_id"] = 123`

3. **Response sent back**.

   * If session data changed, Django updates storage and sets/updates the `sessionid` cookie.

4. **Next request**: Browser sends the `sessionid` cookie → Django restores the session.

---

# 📂 Session Storage Backends

Configured in `settings.py` via `SESSION_ENGINE`:

* `"django.contrib.sessions.backends.db"` → default, stores sessions in DB table (`django_session`).
* `"django.contrib.sessions.backends.cache"` → in-memory cache (faster).
* `"django.contrib.sessions.backends.cached_db"` → hybrid (cache + DB).
* `"django.contrib.sessions.backends.file"` → stores sessions in files.
* `"django.contrib.sessions.backends.signed_cookies"` → stores all session data in the cookie (not recommended for sensitive apps).

---

# 🛠️ Using Sessions in Views

```python
def my_view(request):
    # Add data
    request.session['cart_id'] = 42
    
    # Retrieve data
    cid = request.session.get('cart_id', None)
    
    # Delete data
    if 'cart_id' in request.session:
        del request.session['cart_id']
    
    # Expiry
    request.session.set_expiry(300)  # 5 minutes
```

---

# ⚙️ Important Session Settings

```python
# settings.py

SESSION_COOKIE_NAME = "sessionid"   # name of cookie storing session key
SESSION_COOKIE_AGE = 1209600        # 2 weeks in seconds (default)
SESSION_SAVE_EVERY_REQUEST = False  # save session only if modified
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # True → session ends when browser closes
```

🔎 **What they do:**

* `SESSION_COOKIE_NAME` → Rename if you don’t want the default `sessionid`.
* `SESSION_COOKIE_AGE` → Lifetime of session (default 14 days).
* `SESSION_SAVE_EVERY_REQUEST` → If `True`, resets expiry on every request → keeps active users logged in forever.
* `SESSION_EXPIRE_AT_BROWSER_CLOSE` → Good for security (banks, admin panels).

---

# 🔒 Cookie Security Settings

```python
# settings.py

SESSION_COOKIE_SECURE = True   # Only send cookie over HTTPS
SESSION_COOKIE_HTTPONLY = True # JS can’t read the cookie (protects against XSS)
SESSION_COOKIE_SAMESITE = "Lax"  # Restricts cross-site sending
```

* `SECURE = True` → stops cookie being sent over HTTP.
* `HTTPONLY = True` → makes cookie invisible to JavaScript (`document.cookie`).
* `SAMESITE`:

  * `"Lax"`: sent normally, not with cross-site POSTs → default.
  * `"Strict"`: never sent cross-site → very safe, but can break logins.
  * `"None"`: allows cross-site → must also set `SECURE=True`.

---

# 🎯 Example: “Remember Me” Feature

```python
def login_view(request):
    user = authenticate(request, ...)
    if user:
        login(request, user)
        if not request.POST.get("remember_me", False):
            request.session.set_expiry(0)  # expires on browser close
        else:
            request.session.set_expiry(1209600)  # 2 weeks
```

---

# 🔍 Behind the Scenes: Lifecycle of a Session

1. **User logs in** → Django creates a session in DB with user_id.
2. **`sessionid` cookie sent** to browser (just a random key).
3. **Browser sends cookie back** on every request.
4. **Django looks up session data** in DB/cache.
5. **If expired** → session deleted, user logged out.
6. **If user logs out** → Django clears session from storage + deletes cookie.

---

# 📝 Quick Visual

```
Browser Cookie:   sessionid=abc123
Server Storage:   { "abc123": {"user_id": 5, "cart_id": 42} }
```

On next request:

* Browser → “Here’s sessionid=abc123”
* Server → “Cool, I know that user_id=5 with cart 42”

---

✅ **In summary**:

* **Cookies** are the client-side “keys”.
* **Sessions** are the server-side “locks with data”.
* Together, they let Django “remember” who you are and what you were doing.

---

Do you want me to also **diagram this flow** (request → cookie → session storage → response) with a step-by-step timeline image? It might help you visualize exactly how Django uses cookies + sessions.

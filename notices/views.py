from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.text import slugify
from .models import Notice, Category
from .forms import NoticeForm, CategoryForm


def is_admin(user):
    """Return True if user is staff or superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ---------- STUDENT INTERFACE ----------

def dashboard(request):
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '')

    notices = Notice.objects.filter(status='published')
    notices = [n for n in notices if not n.is_expired]

    if category_slug:
        notices = [
            n for n in notices
            if n.category and (
                n.category.slug == category_slug
                or slugify(n.category.name) == category_slug
            )
        ]

    if query:
        q_lower = query.lower()
        notices = [
            n for n in notices
            if q_lower in n.title.lower() or q_lower in n.content.lower()
        ]

    # ✅ Show ALL notices in the main grid
    latest_notices = notices

    # ✅ Pinned section — up to 6 (adjust to taste)
    important_notices = [n for n in notices if n.is_important][:6]

    categories = Category.objects.all()

    context = {
        'department_name': 'Department of Computer Science',
        'latest_notices': latest_notices,
        'important_notices': important_notices,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
        'total_count': len(notices),
    }
    return render(request, 'notices/dashboard.html', context)


def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk, status='published')
    related = Notice.objects.filter(
        category=notice.category, status='published'
    ).exclude(pk=notice.pk)[:3]
    return render(request, 'notices/notice_detail.html', {
        'notice': notice,
        'related_notices': related,
    })


# ---------- API ----------

def api_search_notices(request):
    """JSON endpoint for live search + category filtering."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    notices = Notice.objects.filter(status='published')
    notices = [n for n in notices if not n.is_expired]

    # Category filter — match by slug OR by slugified name (fallback)
    if category_slug:
        notices = [
            n for n in notices
            if n.category and (
                n.category.slug == category_slug
                or slugify(n.category.name) == category_slug
            )
        ]

    if query:
        q_lower = query.lower()
        notices = [
            n for n in notices
            if q_lower in n.title.lower() or q_lower in n.content.lower()
        ]

    data = []
    # ✅ Return ALL notices (no slicing)
    for n in notices:
        data.append({
            'id': n.pk,
            'title': n.title,
            'content_snippet': n.content[:120] + ('...' if len(n.content) > 120 else ''),
            'category': n.category.name if n.category else None,
            'category_color': n.category.color if n.category else None,
            'author': n.author.get_full_name() or n.author.username,
            'published_at': n.published_at.strftime('%b %d, %Y'),
            'is_important': n.is_important,
            'url': n.get_absolute_url(),
        })

    return JsonResponse({
        'count': len(notices),
        'notices': data,
    })


# ---------- ADMIN INTERFACE ----------

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    now = timezone.now()
    all_notices = Notice.objects.all()
    total = all_notices.count()
    active = sum(1 for n in all_notices if n.is_active)
    expired = sum(1 for n in all_notices if n.is_expired)
    draft = all_notices.filter(status='draft').count()
    users_count = User.objects.count()

    recent = all_notices[:5]

    return render(request, 'notices/admin_dashboard.html', {
        'total_notices': total,
        'active_notices': active,
        'expired_notices': expired,
        'draft_notices': draft,
        'users_count': users_count,
        'recent_notices': recent,
    })


@login_required
@user_passes_test(is_admin)
def manage_notices(request):
    notices = Notice.objects.all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        notices = notices.filter(status=status_filter)
    return render(request, 'notices/manage_notices.html', {
        'notices': notices,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(is_admin)
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            messages.success(request, 'Notice created successfully!')
            return redirect('manage_notices')
    else:
        form = NoticeForm()
    return render(request, 'notices/notice_form.html', {
        'form': form, 'action': 'Create'
    })


@login_required
@user_passes_test(is_admin)
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice updated successfully!')
            return redirect('manage_notices')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notices/notice_form.html', {
        'form': form, 'action': 'Edit', 'notice': notice
    })


@login_required
@user_passes_test(is_admin)
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, 'Notice deleted.')
        return redirect('manage_notices')
    return render(request, 'notices/notice_confirm_delete.html', {'notice': notice})


@login_required
@user_passes_test(is_admin)
def notice_toggle_publish(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.status = 'draft' if notice.status == 'published' else 'published'
    notice.save()
    messages.success(
        request,
        f'Notice {"published" if notice.status == "published" else "unpublished"}.'
    )
    return redirect('manage_notices')


# ---------- CATEGORIES ----------

@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'notices/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'notices/category_form.html', {
        'form': form, 'action': 'Add'
    })


@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'notices/category_form.html', {
        'form': form, 'action': 'Edit', 'category': category
    })


@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'notices/category_confirm_delete.html', {'category': category})
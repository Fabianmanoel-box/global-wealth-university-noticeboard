from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.text import slugify
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Notice, Category
from .forms import NoticeForm, CategoryForm


NOTICES_PER_PAGE = 9
ADMIN_NOTICES_PER_PAGE = 10
ADMIN_CATEGORIES_PER_PAGE = 9


def is_admin(user):
    """Return True if user is staff or superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _auto_publish_due_notices():
    """Flip any 'scheduled' notices whose time has passed to 'published'."""
    now = timezone.now()
    due = Notice.objects.filter(status='scheduled', scheduled_at__lte=now)
    for n in due:
        n.status = 'published'
        n.save(update_fields=['status'])


def _visible_notices(queryset=None):
    """Return notices that are visible to students right now."""
    _auto_publish_due_notices()
    now = timezone.now()
    if queryset is None:
        queryset = Notice.objects.filter(status='published')
    return [
        n for n in queryset
        if not n.is_expired and (not n.scheduled_at or n.scheduled_at <= now)
    ]


# ---------- STUDENT INTERFACE ----------

def dashboard(request):
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    notices = _visible_notices()

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

    is_default_view = not query and not category_slug

    if is_default_view:
        important_notices = [n for n in notices if n.is_important][:6]
        latest_notices = [n for n in notices if not n.is_important]
    else:
        important_notices = [n for n in notices if n.is_important][:6]
        latest_notices = notices

    paginator = Paginator(latest_notices, NOTICES_PER_PAGE)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = Category.objects.all()

    context = {
        'department_name': 'Department of Computer Science',
        'latest_notices': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'important_notices': important_notices,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
        'total_count': len(latest_notices),
    }
    return render(request, 'notices/dashboard.html', context)


def pinned_notices(request):
    _auto_publish_due_notices()
    notices = Notice.objects.filter(status='published', is_important=True)
    notices = _visible_notices(notices)
    categories = Category.objects.all()
    return render(request, 'notices/pinned_notices.html', {
        'department_name': 'Department of Computer Science',
        'notices': notices,
        'categories': categories,
        'total_count': len(notices),
    })


def notice_detail(request, pk):
    _auto_publish_due_notices()
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
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    page_number = request.GET.get('page', 1)

    _auto_publish_due_notices()
    notices = _visible_notices()

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

    is_default_view = not query and not category_slug
    if is_default_view:
        notices = [n for n in notices if not n.is_important]

    paginator = Paginator(notices, NOTICES_PER_PAGE)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    data = []
    for n in page_obj.object_list:
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
        'count': paginator.count,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'notices': data,
    })


# ---------- ADMIN INTERFACE ----------

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    _auto_publish_due_notices()
    all_notices = Notice.objects.all()
    total = all_notices.count()
    active = sum(1 for n in all_notices if n.is_active)
    expired = sum(1 for n in all_notices if n.is_expired)
    scheduled = sum(1 for n in all_notices if n.status == 'scheduled')
    draft = all_notices.filter(status='draft').count()
    users_count = User.objects.count()
    recent = all_notices[:5]

    return render(request, 'notices/admin_dashboard.html', {
        'total_notices': total,
        'active_notices': active,
        'expired_notices': expired,
        'scheduled_notices': scheduled,
        'draft_notices': draft,
        'users_count': users_count,
        'recent_notices': recent,
    })


@login_required
@user_passes_test(is_admin)
def manage_notices(request):
    _auto_publish_due_notices()

    notices = Notice.objects.all()

    status_filter = request.GET.get('status', '')
    if status_filter:
        notices = notices.filter(status=status_filter)

    category_slug = request.GET.get('category', '')
    if category_slug:
        notices = notices.filter(category__slug=category_slug)

    query = request.GET.get('q', '').strip()
    if query:
        notices = notices.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    paginator = Paginator(notices, ADMIN_NOTICES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = Category.objects.all()

    return render(request, 'notices/manage_notices.html', {
        'notices': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'status_filter': status_filter,
        'category_filter': category_slug,
        'query': query,
        'categories': categories,
        'total_count': paginator.count,
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
    if notice.status == 'published':
        notice.status = 'draft'
        notice.scheduled_at = None
    else:
        notice.status = 'published'
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
    categories = Category.objects.all().order_by('name')

    query = request.GET.get('q', '').strip()
    if query:
        categories = categories.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(categories, ADMIN_CATEGORIES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'notices/category_list.html', {
        'categories': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'total_count': paginator.count,
    })


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
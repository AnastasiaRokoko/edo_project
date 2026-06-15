from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404

from .forms import DocumentForm, RegisterForm
from .models import Document, Status


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            group, created = Group.objects.get_or_create(name='Сотрудник')
            user.groups.add(group)

            login(request, user)
            return redirect('document_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def document_list(request):
    query = request.GET.get('q', '')
    status_id = request.GET.get('status', '')

    documents = Document.objects.all()
    statuses = Status.objects.all()

    if query:
        documents = documents.filter(title__icontains=query)

    if status_id:
        documents = documents.filter(status_id=status_id)

    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'statuses': statuses,
        'query': query,
        'selected_status': status_id,
    })


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'documents/document_detail.html', {
        'document': document
    })


@login_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)
            document.author = request.user

            if not document.status:
                document.status = Status.objects.filter(name='Черновик').first()

            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Создание документа'
    })


@login_required
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if document.author != request.user and not request.user.is_staff:
        return redirect('document_list')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)

        if form.is_valid():
            form.save()
            return redirect('document_detail', pk=document.pk)
    else:
        form = DocumentForm(instance=document)

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Редактирование документа'
    })


@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if document.author != request.user and not request.user.is_staff:
        return redirect('document_list')

    if request.method == 'POST':
        document.delete()
        return redirect('document_list')

    return render(request, 'documents/document_confirm_delete.html', {
        'document': document
    })


@login_required
def send_to_approval(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if document.author == request.user or request.user.is_staff:
        status = Status.objects.filter(name='На согласовании').first()
        document.status = status
        document.save()

    return redirect('document_detail', pk=document.pk)


@login_required
def approve_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.user.groups.filter(name='Руководитель').exists() or request.user.is_staff:
        status = Status.objects.filter(name='Утверждён').first()
        document.status = status
        document.save()

    return redirect('document_detail', pk=document.pk)


@login_required
def reject_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.user.groups.filter(name='Руководитель').exists() or request.user.is_staff:
        status = Status.objects.filter(name='Отклонён').first()
        document.status = status
        document.save()

    return redirect('document_detail', pk=document.pk)
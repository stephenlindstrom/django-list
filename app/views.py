from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from .forms import RegistrationForm, AddMemberForm, PrayerRequestForm
from .models import PrayerRequest, GroupPrayerManager

class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name="app/index.html"
    login_url = reverse_lazy("login")


class PersonalPrayerView(LoginRequiredMixin, generic.ListView):
    model = PrayerRequest
    login_url = reverse_lazy("login")
    template_name = "app/personal-prayer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prayer_request_list"] = self.model.objects.filter(user=self.request.user)
        return context


class AddPrayerRequestView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PrayerRequest
    form_class = PrayerRequestForm
    template_name = "app/prayer-request.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("app:prayer-request")
    success_message = "Your request was successfully added."

    def get_form_kwargs(self):
        kwargs = super(AddPrayerRequestView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        groups = form.cleaned_data["groups"]
        if groups:
            for group in groups:
                GroupPrayerManager.objects.create(prayer_request=self.object, group=group)
        return super().form_valid(form)


class RegistrationView(SuccessMessageMixin, CreateView):
    template_name= "app/register.html"
    success_url = reverse_lazy("login")
    form_class = RegistrationForm
    success_message = "Your profile was created successfully"


class CreateGroupView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = Group
    fields = ["name"]
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("app:create-group")
    template_name = "app/create-group.html"

    def form_valid(self, form):
        group = form.save()
        self.request.user.groups.add(group)
        return super().form_valid(form)
    

class GroupListView(LoginRequiredMixin, generic.ListView):
    model = Group
    template_name = "app/group-list.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_list"] = self.request.user.groups.all()
        return context
    
class GroupDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Group
    login_url = reverse_lazy("login")
    template_name = "app/group-detail.html"

    def test_func(self):
        group_id = self.kwargs["pk"]
        return self.request.user.groups.filter(id=group_id).exists()
    
    def get_context_data(self, **kwargs):
        group_id = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        prayer_keys = GroupPrayerManager.objects.filter(group=group_id)
        context["prayer_list"] = []
        for prayer_key in prayer_keys:
            context["prayer_list"].append(prayer_key.prayer_request)
        return context

class AddMemberView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    login_url = reverse_lazy("login")
    template_name = "app/add-member.html"
    form_class = AddMemberForm

    def test_func(self):
        group_id = self.kwargs["group_id"]
        return self.request.user.groups.filter(id=group_id).exists()

    def get_success_url(self):
        group_id = self.kwargs["group_id"]
        return reverse_lazy("app:add-member", kwargs={"group_id":group_id})
    
    def form_valid(self, form):
        group_id = self.kwargs["group_id"]
        new_member_username = form.cleaned_data["username"]
        try:
            new_member = User.objects.get(username=new_member_username)
        except:
            messages.add_message(self.request, messages.ERROR, "Username does not exist")
            return redirect("app:add-member", group_id=group_id)
        group = Group.objects.get(id=group_id)
        new_member.groups.add(group)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs["group_id"]
        context["group_id"] = group_id
        return context
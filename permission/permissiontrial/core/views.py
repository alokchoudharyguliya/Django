from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from core.models import Post

class PostListView(PermissionRequiredMixin, ListView):
    # permission_required = "blog.view_post"
    permission_required=("blog.view_post","blog.add_post") # ---------------> Class based view
    template_name = "post.html"
    model = Post

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
@permission_required("blog.view_post") # -----------> Function based view using a decorator
def post_list_view(request):
    return HttpResponse()


from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import View

from core.models import Post

class PostListView(UserPassesTestMixin, View):
    template_name="post_details.html"

    def test_func(self):
        return self.request.user.has_perm("blog.set_published_status")
    
    def post(self, request, *args, **kwargs):
        post_id=request.POST.get("post_id")
        published_status=request.POST.get("published_status")

        if post_id:
            post=Post.objects.get(pk=post_id)
            post.is_published=bool(published_status)
            post.save()

        return render(request, self.template_name)
from django.template.response import TemplateResponse
from render_block.django import django_render_block


class TemplateBlockResponse(TemplateResponse):
    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        template_block = self._request.GET.get("_renderblock", None)
        # requests with htmx set content as default block name
        if getattr(self._request, "htmx", False) and not template_block:
            template_block = "content"
        if template_block:  # render template block only
            return django_render_block(template, template_block, context, self._request)

        # full template render
        return template.render(context, self._request)

from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        related_name='subtags', 
        on_delete=models.CASCADE
    )
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0057A3', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['parent__name', 'name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return f"{self.parent.name + ' > ' if self.parent else ''}{self.name}"

    @property
    def full_path(self):
        """Returns the full hierarchical path of the tag"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    def get_children(self):
        """Returns all direct child tags"""
        return self.subtags.filter(is_active=True)

    def get_all_descendants(self):
        """Returns all descendant tags (children, grandchildren, etc.)"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

from rest_framework import permissions

class VisibleAndEditableBlogs(permissions.BasePermission):
        
        def has_read_permission(self, request, obj):
            if not request.user.is_authenticated:
                if obj.is_public > 0:
                    return True
                else:
                    return False

            if request.user.is_superuser or request.user == obj.author:
                return True
            elif request.user.group_name == obj.group_name and obj.group_permission > 0:
                return True
            elif request.user.is_authenticated and obj.authenticated_permission > 0:
                    return True
            elif obj.is_public > 0:
                return True
            else:
                return False
        
        def has_edit_permission(self, request, obj):
            if not request.user.is_authenticated:
                return False
            if request.user.is_superuser or request.user == obj.author:
                return True
            elif request.user.group_name == obj.group_name and obj.group_permission == 2:
                return True
            elif request.user.is_authenticated and obj.authenticated_permission == 2:
                    return True
            else:
                return False
        
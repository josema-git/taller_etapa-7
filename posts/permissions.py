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
            elif request.user.team == obj.team and obj.group_permission > 0:
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
            elif request.user.team == obj.team and obj.group_permission == 2:
                return True
            elif request.user.is_authenticated and obj.authenticated_permission == 2:
                    return True
            else:
                return False
        
        def permission_level(self, request, obj):
            if not request.user.is_authenticated:
                return obj.is_public

            if request.user.is_superuser or request.user == obj.author:
                return 3
            elif request.user.team == obj.team and obj.group_permission > 0:
                return obj.group_permission + 1
            elif obj.authenticated_permission > 0:
                return obj.authenticated_permission + 1
            elif obj.is_public > 0:
                return obj.is_public + 1
            else:
                return obj.is_public
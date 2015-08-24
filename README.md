# python-appstream

If you want to parse AppStream files in Python you probably should
just install libappstream-glib, and use the GObjectIntrospection bindings
for that. AppStreamGlib is a much better library than this and handles
many more kinds of component.

If AppStreamGlib is not available to you (e.g. you're trying to run in an
OpenShift instance on RHEL 6.2), this project might be somewhat useful.

Contributors welcome, either adding new functionality or fixing bugs.

See also: http://www.freedesktop.org/software/appstream/docs/


class BlogPyAddons:

    @staticmethod
    def add_blog_options(group):
        group.addoption('--blog-project-name', default=None, action='store', help='Change project name for the entire Run')
        group.addoption('--blog-env', default=None, action='store', help='Set env for the entire Run')
        group.addoption('--blog-base-url', default=None, action='store', help='Set base url for the entire Run')

    @staticmethod
    def add_blog_markers(config):
        config.addinivalue_line('markers', 'blog_description')
        config.addinivalue_line('markers', 'blog_info')
        config.addinivalue_line('markers', 'blog_link')
        config.addinivalue_line('markers', 'blog_known_bug')

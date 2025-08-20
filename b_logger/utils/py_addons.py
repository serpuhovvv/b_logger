
class BlogPyAddons:

    @staticmethod
    def add_blog_options(parser, group):
        group.addoption('--blog_base_url', default=None, action='store', help='')
        group.addoption('--blog_env', default=None, action='store', help='')

    @staticmethod
    def add_blog_markers(config):
        config.addinivalue_line('markers', 'blog_description')
        config.addinivalue_line('markers', 'blog_info')
        config.addinivalue_line('markers', 'blog_link')
        config.addinivalue_line('markers', 'blog_known_bug')

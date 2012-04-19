import unittest
from pyramid import testing

class TestManageCatalog(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import ManageCatalog
        return ManageCatalog(context, request)

    def test_view(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.mgmt_path = lambda *arg: '/manage'
        inst = self._makeOne(context, request)
        result = inst.view()
        self.assertEqual(result['cataloglen'], 0)

    def test_reindex(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.mgmt_path = lambda *arg: '/manage'
        inst = self._makeOne(context, request)
        result = inst.reindex()
        self.assertEqual(result.location, '/manage')
        self.assertEqual(context.reindexed, True)

    def test_refresh(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.mgmt_path = lambda *arg: '/manage'
        inst = self._makeOne(context, request)
        result = inst.refresh()
        self.assertEqual(result.location, '/manage')
        self.assertEqual(context.refreshed, True)

class Test_principals_widget(unittest.TestCase):
    def _makeOne(self, node, kw):
        from ..views import principals_widget
        return principals_widget(node, kw)

    def test_it(self):
        from ...interfaces import IFolder
        request = testing.DummyRequest()
        context = testing.DummyResource(__provides__=IFolder)
        services = testing.DummyResource()
        users = testing.DummyResource()
        groups = testing.DummyResource()
        group = testing.DummyResource()
        group.__objectid__ = 1
        user = testing.DummyResource()
        user.__objectid__ = 2
        groups['group'] = group
        users['users'] = user
        principals = testing.DummyResource()
        principals['groups'] = groups
        principals['users'] = users
        services['principals'] = principals
        context['__services__'] = services
        services['principals'] = principals
        context['__services__'] = services
        request.context = context
        kw = dict(request=request)
        widget = self._makeOne(None, kw)
        self.assertEqual(
            widget.values,
            ({'values': [('1', 'group')], 'label': 'Groups'},
             {'values': [('2', 'users')], 'label': 'Users'})
            )

class TestSearchCatalogView(unittest.TestCase):
    def _makeOne(self, request):
        from ..views import SearchCatalogView
        return SearchCatalogView(request)

    def test_search_success(self):
        request = testing.DummyRequest()
        request.mgmt_path = lambda *arg, **kw: '/mg'
        inst = self._makeOne(request)
        resp = inst.search_success({'a':1})
        self.assertEqual(request.session['catalogsearch.appstruct'], {'a':1})
        self.assertEqual(resp.location, '/mg')

    def test_show_no_appstruct(self):
        request = testing.DummyRequest()
        form = DummyForm()
        inst = self._makeOne(request)
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': (),
                                  'form':'form'})

    def test_show_with_appstruct_no_permission(self):
        request = testing.DummyRequest()
        appstruct = {'cqe_expression':'abc',
                     'permitted':{'permission':'', 'principals':()}
                     }
        request.session['catalogsearch.appstruct'] = appstruct
        def query(expr, permitted):
            self.assertEqual(expr, 'abc')
            self.assertEqual(permitted, None)
            return 0, (), None
        request.query_catalog = query
        form = DummyForm()
        inst = self._makeOne(request)
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': [('', 'No results')],
                                  'form':'form'})
        self.assertEqual(request.session['_f_success'], ['Query succeeded'])

    def test_show_with_appstruct_permission(self):
        request = testing.DummyRequest()
        appstruct = {'cqe_expression':'abc',
                     'permitted':{'permission':'view', 'principals':()}
                     }
        request.session['catalogsearch.appstruct'] = appstruct
        def query(expr, permitted):
            self.assertEqual(expr, 'abc')
            self.assertEqual(permitted, ((), 'view'))
            return 0, (), None
        request.query_catalog = query
        form = DummyForm()
        inst = self._makeOne(request)
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': [('', 'No results')],
                                  'form':'form'})
        self.assertEqual(request.session['_f_success'], ['Query succeeded'])

    def test_show_with_appstruct_query_exception(self):
        request = testing.DummyRequest()
        appstruct = {'cqe_expression':'abc',
                     'permitted':{'permission':'view', 'principals':()}
                     }
        request.session['catalogsearch.appstruct'] = appstruct
        def query(expr, permitted):
            raise ValueError('hello')
        request.query_catalog = query
        form = DummyForm()
        inst = self._makeOne(request)
        inst.logger = DummyLogger()
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': (),
                                  'form':'form'})
        self.assertEqual(request.session['_f_error'],
                         ['Query failed (ValueError: hello)'])

class DummyForm(object):
    def render(self, appstruct):
        return 'form'

class DummyLogger(object):
    def exception(self, msg):
        pass
        
class DummyCatalog(object):
    def __init__(self):
        self.objectids = ()

    def reindex(self):
        self.reindexed = True

    def refresh(self, registry):
        self.refreshed = True
        
        

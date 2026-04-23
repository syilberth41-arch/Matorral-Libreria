"""Tests for auth blueprint."""


class TestRegistration:
    def test_register_page_loads(self, client):
        resp = client.get('/auth/register')
        assert resp.status_code == 200
        assert 'Crear Cuenta' in resp.data.decode()

    def test_register_success(self, client, db):
        resp = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'securepass1',
            'confirm_password': 'securepass1',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert 'Registro exitoso' in resp.data.decode()

    def test_register_password_mismatch(self, client, db):
        resp = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'securepass1',
            'confirm_password': 'different',
        }, follow_redirects=True)
        assert 'no coinciden' in resp.data.decode()

    def test_register_short_password(self, client, db):
        resp = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'short',
            'confirm_password': 'short',
        }, follow_redirects=True)
        assert 'al menos 8 caracteres' in resp.data.decode()

    def test_register_duplicate_email(self, client, db, sample_user):
        resp = client.post('/auth/register', data={
            'username': 'another',
            'email': 'test@test.com',
            'password': 'securepass1',
            'confirm_password': 'securepass1',
        }, follow_redirects=True)
        assert 'ya está registrado' in resp.data.decode()


class TestLogin:
    def test_login_page_loads(self, client):
        resp = client.get('/auth/login')
        assert resp.status_code == 200
        assert 'Iniciar Sesión' in resp.data.decode()

    def test_login_success(self, client, db, sample_user):
        resp = client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password123',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert 'Bienvenido' in resp.data.decode()

    def test_login_invalid_credentials(self, client, db, sample_user):
        resp = client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'wrongpass',
        }, follow_redirects=True)
        assert 'inválidas' in resp.data.decode()

    def test_logout(self, logged_in_client):
        resp = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert resp.status_code == 200
        assert 'cerrada' in resp.data.decode()


class TestProfile:
    def test_profile_requires_login(self, client, db):
        resp = client.get('/auth/profile', follow_redirects=True)
        assert 'Iniciar Sesión' in resp.data.decode()

    def test_profile_shows_info(self, logged_in_client, sample_user):
        resp = logged_in_client.get('/auth/profile')
        assert resp.status_code == 200
        assert 'testuser' in resp.data.decode()


class Test2FA:
    def test_setup_2fa_page(self, logged_in_client, sample_user):
        resp = logged_in_client.get('/auth/setup-2fa')
        assert resp.status_code == 200
        assert 'Configurar 2FA' in resp.data.decode()

    def test_verify_2fa_redirect_without_session(self, client, db):
        resp = client.get('/auth/verify-2fa', follow_redirects=True)
        assert 'Iniciar Sesión' in resp.data.decode()

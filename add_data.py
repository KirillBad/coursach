from website import create_app, db
from website.models import User, Role

app = create_app()

with app.app_context():
    # db.drop_all()
    admin_role = Role(name='admin')
    user_role = Role(name='user')


    db.session.add_all([admin_role, user_role])
    db.session.commit() 


    admin = User(login='kirillbad', password_hash='scrypt:32768:8:1$T7aWszDpoq1TphZm$3d780ce93e1722a7208431e3a878c1b93d17c90209672bb2e5259670037e66a1c3cdb5e86670a2a1b379033effeea49924bcc60f1680ca7746c0dc81584ca308', role=admin_role)


    db.session.add(admin)
    db.session.commit() 
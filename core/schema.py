import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token

from .models import Task

class UserType(DjangoObjectType):
    class Meta:
        model = User

class TaskType(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = Task

    def resolve_user(self, info):
        return self.created_by  # Assuming 'created_by' is the ForeignKey field in Task model.

class CreateUserMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, username, password, email=None, first_name=None, last_name=None):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        return CreateUserMutation(user=user)

class LoginUserMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    token = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, password):
        user = authenticate(info.context, username=username, password=password)
        if user is not None:
            login(info.context, user)
            token, created = Token.objects.get_or_create(user=user)
            return LoginUserMutation(success=True, message='Login successful', user=user, token=token.key)
        else:
            raise Exception('Invalid credentials')

class CreateTaskMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        due_date = graphene.Date(required=True)

    task = graphene.Field(TaskType)

    def mutate(self, info, title, description, due_date):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('You must be logged in to create a task.')

        task = Task(title=title, description=description, due_date=due_date, created_by=user)
        task.save()

        return CreateTaskMutation(task=task)

class Mutation(graphene.ObjectType):
    create_task = CreateTaskMutation.Field()
    create_user = CreateUserMutation.Field()
    login_user = LoginUserMutation.Field()

class Query(graphene.ObjectType):
    tasks = graphene.List(TaskType)
    task_by_id = graphene.Field(TaskType, id=graphene.Int())
    task_by_title = graphene.Field(TaskType, title=graphene.String())
    current_user = graphene.Field(UserType)

    def resolve_tasks(self, info):
        return Task.objects.all()

    def resolve_task_by_id(self, info, id):
        return Task.objects.get(id=id)

    def resolve_task_by_title(self, info, title):
        return Task.objects.get(title=title)

    def resolve_current_user(self, info):
        return info.context.user

schema = graphene.Schema(query=Query, mutation=Mutation)

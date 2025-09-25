# schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Book

class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "published_year")


class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)
    book_by_id = graphene.Field(BookType, id=graphene.Int(required=True))

    def resolve_all_books(root, info):
        return Book.objects.all()  # resolver for all_books

    def resolve_book_by_id(root, info, id):
        return Book.objects.get(pk=id)  # resolver for book_by_id

class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author = graphene.String(required=True)
        published_year = graphene.Int(required=True)

    book = graphene.Field(BookType)

    def mutate(root, info, title, author, published_year):
        book = Book(title=title, author=author, published_year=published_year)
        book.save()
        return CreateBook(book=book)

class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

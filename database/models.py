from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    seniority: Mapped[str | None] = mapped_column()
    remote_allowed: Mapped[bool] = mapped_column()
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    salary: Mapped[int | None] = mapped_column()
    habr_id: Mapped[int] = mapped_column(unique=True)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(30), unique=True)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str] = mapped_column(String(30), unique=True)


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_name: Mapped[str] = mapped_column(unique=True)

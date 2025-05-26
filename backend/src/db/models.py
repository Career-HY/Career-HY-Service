# models.py
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, ForeignKey, Table, Text, Enum, DECIMAL, func, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ——— 프로필-카탈로그 매핑 테이블 ———
course_catalog_mapping = Table(
    "course_catalog_mapping", Base.metadata,
    Column("profile_id", String(36), ForeignKey("profile.member_id"), primary_key=True),
    Column("course_catalog_id", Integer, ForeignKey("course_catalogs.id"), primary_key=True),
)

# ——— 공고-회원 매핑 테이블 ———
job_posting_mapping = Table(
    "job_posting_mapping", Base.metadata,
    Column("job_posting_id", String(36), ForeignKey("job_posting.id"), primary_key=True),
    Column("member_id", String(36), ForeignKey("member.id"), primary_key=True),
)


class Member(Base):
    __tablename__ = "member"
    id          = Column(String(36), primary_key=True)
    email       = Column(String(255), unique=True, nullable=False)
    pwd         = Column(String(255), nullable=False)
    signup_date = Column(DateTime, nullable=False, server_default=func.now())

    # ——— 멤버-프로필 참조 ———
    profile = relationship("Profile", back_populates="member", uselist=False)

    # ——— 멤버-공고 참조 ———
    job_postings = relationship(
        "JobPosting",
        secondary=job_posting_mapping,
        back_populates="members"
    )


class Profile(Base):
    __tablename__ = "profile"
    member_id  = Column(String(36), ForeignKey("member.id"), primary_key=True)
    grade      = Column(String(10), nullable=True)
    department = Column(String(50), nullable=True)

    # ——— 프로필-멤버 참조 ———
    member = relationship("Member", back_populates="profile")

    # ——— 프로필-동아리 참조 ———
    club_activities = relationship("ClubActivity", back_populates="profile", cascade="all, delete-orphan")
    
    # ——— 프로필-관심직무 참조 ———
    job_interests   = relationship("JobInterest", back_populates="profile", cascade="all, delete-orphan")

    # ——— 프로필-카탈로그 참조 ———
    course_catalogs = relationship(
        "CourseCatalog",
        secondary=course_catalog_mapping,
        back_populates="profiles"
    )


class ClubActivity(Base):
    __tablename__ = "club_activity"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String(36), ForeignKey("profile.member_id"))
    content    = Column(String(255))

    # ——— 동아리-프로필 참조 ———
    profile = relationship("Profile", back_populates="club_activities")


class JobInterest(Base):
    __tablename__ = "job_interests"
    profile_id = Column(String(36), ForeignKey("profile.member_id"), primary_key=True)
    interest   = Column(String(255), primary_key=True)

    # ——— 관심직무-프로필 참조 ———
    profile = relationship("Profile", back_populates="job_interests")


class CourseCatalog(Base):
    __tablename__ = "course_catalogs"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    academic_year         = Column(Integer, nullable=True)
    section               = Column(Integer, nullable=True)
    credit_type           = Column(String(50), nullable=True)
    credit_units          = Column(String(50), nullable=True)   
    domain                = Column(String(100), nullable=True)
    course_number         = Column(String(50), nullable=True)
    course_code           = Column(String(50), nullable=True)
    old_course_name       = Column(String(255), nullable=True)
    course_name           = Column(String(255), nullable=True)
    course_guide          = Column(Text, nullable=True)
    accreditation_type    = Column(String(100), nullable=True)
    degree_program        = Column(String(100), nullable=True)
    instructor            = Column(String(100), nullable=True)
    total_credits         = Column(DECIMAL(3, 1), nullable=True)
    lecture_credits       = Column(DECIMAL(3, 1), nullable=True)
    lab_credits           = Column(DECIMAL(3, 1), nullable=True)
    course_category       = Column(String(100), nullable=True)
    enrollment_capacity   = Column(String(50), nullable=True)
    class_format          = Column(String(100), nullable=True)
    class_time            = Column(String(100), nullable=True)
    classroom             = Column(String(100), nullable=True)
    completion_restriction= Column(String(5),  nullable=True)   
    detailed_info         = Column(Text, nullable=True)
    core_competency       = Column(Text, nullable=True)
    offering_department   = Column(String(100), nullable=True)
    course_overview       = Column(Text, nullable=True)
    course_objectives     = Column(Text, nullable=True)
    week1_plan            = Column(Text, nullable=True)
    week2_plan            = Column(Text, nullable=True)
    week3_plan            = Column(Text, nullable=True)
    week4_plan            = Column(Text, nullable=True)
    week5_plan            = Column(Text, nullable=True)
    week6_plan            = Column(Text, nullable=True)
    week7_plan            = Column(Text, nullable=True)
    week8_plan            = Column(Text, nullable=True)
    week9_plan            = Column(Text, nullable=True)
    week10_plan           = Column(Text, nullable=True)
    week11_plan           = Column(Text, nullable=True)
    week12_plan           = Column(Text, nullable=True)
    week13_plan           = Column(Text, nullable=True)
    week14_plan           = Column(Text, nullable=True)
    week15_plan           = Column(Text, nullable=True)
    week16_plan           = Column(Text, nullable=True)

    # ——— 카탈로그-프로필 참조 ———
    profiles = relationship(
        "Profile",
        secondary=course_catalog_mapping,
        back_populates="course_catalogs"
    )


class JobPosting(Base):
    __tablename__ = "job_posting"

    id            = Column(String(36), primary_key=True, server_default=text("UUID()"))
    title         = Column(String(255), nullable=True)
    start_date    = Column(DateTime,     nullable=True)
    deadline      = Column(DateTime,     nullable=True)
    is_active     = Column(Boolean,      nullable=False, default=True)
    url           = Column(String(255),  nullable=True)
    crawling_time = Column(DateTime,     nullable=False, server_default=func.now())

    # ——— 공고-멤버 참조 ———
    members = relationship(
        "Member",
        secondary=job_posting_mapping,
        back_populates="job_postings"
    )

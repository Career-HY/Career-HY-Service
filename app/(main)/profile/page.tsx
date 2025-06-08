import {
  type CourseCatalogRead,
  type CourseCatalogSearchResult,
} from "@/lib/api/generated/model";
import type { Course } from "components/profile/CourseSearch";

interface Course {
  id: number;
  course_name: string;
  course_code: string;
  credit_units: string;
  instructor: string;
  offering_department: string;
}

const mapCourseCatalogToCourse = (
  catalog: CourseCatalogRead | CourseCatalogSearchResult
): Course => {
  return {
    id: catalog.id,
    course_name: catalog.course_name || "",
    course_code: catalog.course_code || "",
    credit_units: catalog.credit_units || "",
    instructor: catalog.instructor || "",
    offering_department: catalog.offering_department || "",
  };
};

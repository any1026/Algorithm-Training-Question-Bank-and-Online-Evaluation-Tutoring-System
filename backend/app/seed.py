from app.core.database import SessionLocal, init_db
from app.schemas.problem import ProblemCreate, TestCaseCreate
from app.services.problems import create_problem, list_problems


def seed() -> None:
    init_db()
    with SessionLocal() as db:
        _, total = list_problems(db, limit=1)
        if total:
            print("Seed skipped: problems already exist.")
            return

        create_problem(
            ProblemCreate(
                title="A + B Problem",
                difficulty="easy",
                description="Read two integers and output their sum.",
                input_description="Two integers a and b.",
                output_description="One integer, the sum of a and b.",
                constraints="-10^9 <= a, b <= 10^9",
                sample_input="1 2\n",
                sample_output="3\n",
                tags=["basic", "math"],
                test_cases=[
                    TestCaseCreate(input_data="1 2\n", expected_output="3\n", is_sample=True, sort_order=1),
                    TestCaseCreate(input_data="-5 8\n", expected_output="3\n", sort_order=2),
                ],
            ),
            db,
        )
        print("Seed completed.")


if __name__ == "__main__":
    seed()

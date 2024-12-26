from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta, timezone
import random

# revision identifiers, used by Alembic.
revision = 'add_initial_data'
down_revision = '54413cc9dd16'
branch_labels = None
depends_on = None


def random_date(start, end):
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def upgrade() -> None:
    connection = op.get_bind()

    # Insert user data
    connection.execute(
        sa.text("""
        INSERT INTO users (tg_id, name, timezone) 
        VALUES (:tg_id, :name, :timezone)
        """),
        {"tg_id": 722538762, "name": "Aleksey", "timezone": 7}
    )

    user_id = 722538762

    # Tables to fill with random data
    tables = [
        'alcohol', 'charity', 'cigarettes', 'cosmetics_and_care', 'debts', 'devices',
        'eating_out', 'education', 'entertainment', 'friends_and_family', 'health',
        'household', 'pets', 'products', 'purchases', 'services', 'sport', 'transport', 'travel'
    ]

    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)

    for table in tables:
        data = []
        for _ in range(10):
            data.append({
                "user_id": user_id,
                "summ": round(random.uniform(10, 10000), 2),
                "updated_at": random_date(start_date, end_date)
            })

        connection.execute(
            sa.text(f"""
            INSERT INTO {table} (user_id, summ, updated_at) 
            VALUES (:user_id, :summ, :updated_at)
            """),
            data
        )
    op.execute("""
           INSERT INTO monthly_limits (
               user_id, alcohol, charity, debts, household, eating_out, health, 
               cosmetics_and_care, education, pets, purchases, products, travel, 
               entertainment, friends_and_family, cigarettes, sport, devices, 
               transport, services
           ) VALUES (
               722538762,
               {0}, {1}, {2}, {3}, {4}, {5}, {6}, 
               {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}
           )
       """.format(
        random.randint(0, 30000),  # alcohol
        random.randint(0, 30000),  # charity
        random.randint(0, 30000),  # debts
        random.randint(0, 30000),  # household
        random.randint(0, 30000),  # eating_out
        random.randint(0, 30000),  # health
        random.randint(0, 30000),  # cosmetics_and_care
        random.randint(0, 30000),  # education
        random.randint(0, 30000),  # pets
        random.randint(0, 30000),  # purchases
        random.randint(0, 30000),  # products
        random.randint(0, 30000),  # travel
        random.randint(0, 30000),  # entertainment
        random.randint(0, 30000),  # friends_and_family
        random.randint(0, 30000),  # cigarettes
        random.randint(0, 30000),  # sport
        random.randint(0, 30000),  # devices
        random.randint(0, 30000),  # transport
        random.randint(0, 30000)  # services
    ))

def downgrade() -> None:
    connection = op.get_bind()

    # Delete random data
    tables = [
        'alcohol', 'charity', 'cigarettes', 'cosmetics_and_care', 'debts', 'devices',
        'eating_out', 'education', 'entertainment', 'friends_and_family', 'health',
        'household', 'pets', 'products', 'purchases', 'services', 'sport', 'transport', 'travel', 'monthly_limits'
    ]

    for table in tables:
        connection.execute(sa.text(f"DELETE FROM {table} WHERE user_id = :user_id"), {"user_id": 722538762})

    # Delete user data
    connection.execute(sa.text("DELETE FROM users WHERE tg_id = :tg_id"), {"tg_id": 722538762})

"""${message}"""

${revision_id} = "${revision_id}"
down_revision = ${down_revision!r}
branch_labels = ${branch_labels!r}
depends_on = ${depends_on!r}


from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

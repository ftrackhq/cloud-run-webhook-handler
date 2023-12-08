import typing
import logging
import datetime
import OS

from fastapi import FastAPI, Header
from pydantic import BaseModel
import ftrack_api


class Metadata(BaseModel):
    date: str
    resource_id: str
    server_url: str


class Entity(BaseModel):
    id: typing.List[str]
    entity_type: str
    operation: str
    new: dict
    old: dict


class EntityEvent(BaseModel):
    id: str
    metadata: Metadata
    entity: Entity


# CONSTANTS.
PENDING_REVIEW = '44dded64-4164-11df-9218-0019bb4983d8'
APPROVED = '44de097a-4164-11df-9218-0019bb4983d8'
LIST_DAILIES = '77b9ab82-07c2-11e4-ba66-04011030cf01'
LIST_DELIVERY = '712f0fee-ead3-11e2-846c-f23c91dfaa16'


app = FastAPI()
logging.basicConfig(level=logging.INFO)


def add_version_to_list(version_id, project_id, list_name, category_id):
    session = ftrack_api.Session()

    dailies_list = session.query(
        f'List where name is "{list_name}" and project_id is "{project_id}"'
    ).first()

    if not dailies_list:
        logging.info(f"Creating new list: {list_name}")
        dailies_list = session.create('AssetVersionList', {
            'name': list_name,
            'project_id': project_id,
            'category_id': category_id
        })

    list_object = session.query(
        f'ListObject where list_id is "{dailies_list["id"]}" and entity_id is "{version_id}"'
    ).first()

    if not list_object:
        session.create('ListObject', {
            'list_id': dailies_list['id'],
            'entity_id': version_id,
            'entity_type': 'AssetVersion'
        })

        session.commit()


@app.post("/")
def index(event: EntityEvent, ftrack_secret: typing.Annotated[str | None, Header()] = None):
    if ftrack_secret is None or ftrack_secret != os.environ.get('FTRACK_SECRET'):
        return "Invalid secret"

    if (
        event.entity.entity_type == 'AssetVersion' and
        event.entity.operation == 'update' and
        event.entity.new['status_id'] != event.entity.old['status_id']
    ):
        logging.info(f"AssetVersion changed status from {event.entity.old['status_id']} to {event.entity.new['status_id']}")

        if event.entity.new['status_id'] == PENDING_REVIEW:
            logging.info("AssetVersion is now 'Pending review', lets add it to todays review list.")

            add_version_to_list(
                event.entity.new['id'],
                event.entity.new['project_id'],
                f"Dailies {datetime.datetime.today().strftime('%Y-%m-%d')}",
                category_id=LIST_DAILIES
            )

            return "Version was added to dailies list."
        
        elif event.entity.new['status_id'] == APPROVED:
            logging.info("AssetVersion is now 'Approved', lets add it to the delivery list.")

            today = datetime.datetime.today()
            next_friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
            if today.weekday() == 4:
                next_friday = today + datetime.timedelta(7)

            add_version_to_list(
                event.entity.new['id'],
                event.entity.new['project_id'],
                f"Weekly Delivery {next_friday.strftime('%Y-%m-%d')}",
                category_id=LIST_DELIVERY
            )

            return "Version was added to delivery list."

    return "Did nothing."

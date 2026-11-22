"""End-to-end backend tests for the NEXUS orchestration and approval flow.

Run with:
    .\\.venv\\Scripts\\python.exe -m unittest tests.test_flow -v
"""

import json
import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
os.environ["DATABASE_URL"] = "sqlite:///./test_nexus.db"
os.environ["DEMO_MODE"] = "true"
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_ALLOWED_CHAT_IDS"] = ""
os.environ["TELEGRAM_DEFAULT_CHAT_ID"] = ""
sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, SessionLocal, engine, init_db  # noqa: E402
from app.integrations import telegram_bot  # noqa: E402
from app.models import TelegramChat  # noqa: E402
from app.services import approval_service, mission_service  # noqa: E402
from app.services.approval_service import ApprovalError  # noqa: E402

OBJECTIVE = "Organize a technical workshop for 100 students within 10 days."


class NexusFlowTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(engine)
        init_db()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(engine)
        engine.dispose()
        db_path = BACKEND_DIR / "test_nexus.db"
        if db_path.exists():
            db_path.unlink()

    async def _new_mission(self, db, source="telegram", chat="12345", objective=OBJECTIVE):
        mission = mission_service.create_mission(
            db, objective, source=source, source_chat_id=chat
        )
        await mission_service.run_mission(db, mission)
        db.refresh(mission)
        return mission

    async def test_software_deployment_demo_is_domain_specific(self):
        db = SessionLocal()
        try:
            objective = "Deploy the customer portal to production within 14 days."
            mission = await self._new_mission(db, objective=objective)
            research = json.loads(mission.agent_results[0].output)
            planning = json.loads(mission.agent_results[1].output)
            communication = json.loads(mission.agent_results[2].output)

            self.assertEqual(research["domain"], "software_deployment")
            self.assertEqual(planning["domain"], "software_deployment")

            titles = [task["title"] for task in planning["tasks"]]
            for expected in [
                "Define deployment architecture and environment requirements",
                "Configure CI/CD pipeline",
                "Prepare environment variables and secrets",
                "Run automated tests and security checks",
                "Deploy to staging and validate",
                "Deploy to production with rollback and monitoring plans",
            ]:
                self.assertIn(expected, titles)

            combined = " ".join(
                titles
                + [task["description"] for task in planning["tasks"]]
                + [communication["announcement"]]
            ).lower()
            for forbidden in [
                "venue",
                "agenda",
                "registration",
                "workshop",
                "participants",
            ]:
                self.assertNotIn(forbidden, combined)

            self.assertIn("deployment plan", communication["announcement"].lower())
            self.assertEqual(planning["objective"], objective)
            self.assertEqual(communication["objective"], objective)
        finally:
            db.close()

    async def test_event_demo_keeps_event_tasks(self):
        db = SessionLocal()
        try:
            mission = await self._new_mission(db)
            planning = json.loads(mission.agent_results[1].output)
            titles = [task["title"] for task in planning["tasks"]]
            self.assertEqual(planning["domain"], "event")
            self.assertIn("Secure venue, budget and resources", titles)
            self.assertIn("Publish announcement and open registration", titles)
            combined = " ".join(titles).lower()
            self.assertNotIn("ci/cd", combined)
            self.assertNotIn("deployment", combined)
        finally:
            db.close()

    async def test_marketing_demo_avoids_event_tasks(self):
        db = SessionLocal()
        try:
            objective = (
                "Launch a developer newsletter for 5,000 subscribers within 21 days."
            )
            mission = await self._new_mission(db, objective=objective)
            planning = json.loads(mission.agent_results[1].output)
            self.assertEqual(planning["domain"], "marketing_campaign")
            combined = " ".join(
                [task["title"] for task in planning["tasks"]]
                + [task["description"] for task in planning["tasks"]]
            ).lower()
            self.assertIn("campaign", combined)
            for forbidden in ["venue", "agenda", "registration", "workshop"]:
                self.assertNotIn(forbidden, combined)
        finally:
            db.close()

    async def test_data_migration_demo_is_domain_specific(self):
        db = SessionLocal()
        try:
            objective = (
                "Migrate the billing database to PostgreSQL within 30 days."
            )
            mission = await self._new_mission(db, objective=objective)
            planning = json.loads(mission.agent_results[1].output)
            self.assertEqual(planning["domain"], "data_migration")
            combined = " ".join(
                [task["title"] for task in planning["tasks"]]
                + [task["description"] for task in planning["tasks"]]
            ).lower()
            self.assertIn("cutover", combined)
            for forbidden in ["venue", "agenda", "registration"]:
                self.assertNotIn(forbidden, combined)
        finally:
            db.close()

    async def test_pipeline_produces_connected_agent_outputs(self):
        db = SessionLocal()
        try:
            mission = await self._new_mission(db)
            self.assertEqual(mission.status, "awaiting_approval")
            self.assertEqual(len(mission.agent_results), 3)
            self.assertEqual(len(mission.tasks), 6)
            self.assertEqual(len(mission.approvals), 1)
            self.assertEqual(mission.approvals[0].status, "pending")

            names = [r.agent_name for r in mission.agent_results]
            self.assertEqual(names, ["research", "planning", "communication"])

            research = json.loads(mission.agent_results[0].output)
            planning = json.loads(mission.agent_results[1].output)
            communication = json.loads(mission.agent_results[2].output)

            self.assertTrue(research["requirements"])
            self.assertEqual(research["source"], "demo")
            self.assertTrue(planning["tasks"])
            self.assertEqual(
                planning["tasks"][0]["title"], mission.tasks[0].title
            )
            self.assertIn(OBJECTIVE.rstrip("."), communication["announcement"])
            self.assertEqual(
                communication["action"]["content"],
                communication["announcement"],
            )
            self.assertEqual(
                mission.approvals[0].content, communication["announcement"]
            )
        finally:
            db.close()

    async def test_approval_delivers_once_and_blocks_duplicates(self):
        calls = []

        async def fake_send(text, chat_id):
            calls.append((text, chat_id))
            return "4242"

        telegram_bot.telegram_manager.running = True
        telegram_bot.telegram_manager.send_message = fake_send
        db = SessionLocal()
        try:
            mission = await self._new_mission(db)
            approval_id = mission.approvals[0].id

            result = await approval_service.approve(db, approval_id)
            self.assertEqual(result["status"], "sent")
            self.assertEqual(result["telegram_message_id"], "4242")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1], 12345)

            db.refresh(mission)
            self.assertEqual(mission.status, "completed")

            with self.assertRaises(ApprovalError) as ctx:
                await approval_service.approve(db, approval_id)
            self.assertEqual(ctx.exception.status_code, 409)
            self.assertEqual(len(calls), 1, "duplicate send must be blocked")
        finally:
            telegram_bot.telegram_manager.running = False
            db.close()

    async def test_known_chat_is_used_as_delivery_fallback(self):
        calls = []

        async def fake_send(text, chat_id):
            calls.append((text, chat_id))
            return "7777"

        telegram_bot.telegram_manager.running = True
        telegram_bot.telegram_manager.send_message = fake_send
        db = SessionLocal()
        try:
            db.query(TelegramChat).delete()
            db.add(TelegramChat(chat_id="55555", first_name="Operator"))
            db.commit()

            mission = await self._new_mission(db, source="web", chat=None)
            self.assertEqual(mission.approvals[0].target_chat_id, "55555")

            result = await approval_service.approve(db, mission.approvals[0].id)
            self.assertEqual(result["status"], "sent")
            self.assertEqual(calls[0][1], 55555)
        finally:
            telegram_bot.telegram_manager.running = False
            db.query(TelegramChat).delete()
            db.commit()
            db.close()

    async def test_rejected_action_is_never_sent(self):
        calls = []

        async def fake_send(text, chat_id):
            calls.append((text, chat_id))
            return "9999"

        telegram_bot.telegram_manager.running = True
        telegram_bot.telegram_manager.send_message = fake_send
        db = SessionLocal()
        try:
            mission = await self._new_mission(db)
            approval_id = mission.approvals[0].id

            result = approval_service.reject(db, approval_id)
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(len(calls), 0)

            db.refresh(mission)
            self.assertEqual(mission.status, "rejected")

            with self.assertRaises(ApprovalError):
                await approval_service.approve(db, approval_id)
            self.assertEqual(len(calls), 0, "rejected action must never be sent")
        finally:
            telegram_bot.telegram_manager.running = False
            db.close()


if __name__ == "__main__":
    unittest.main()

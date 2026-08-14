import asyncio
import logging
from app.main import start_camera, stop_camera, run_in_thread, generate_mjpeg_frames

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CameraTest")

async def run_camera_test_sequence():
    logger.info("=========================================")
    logger.info("TESTING PHASE 6.5 CAMERA CONTROL FLOW")
    logger.info("=========================================")

    # Test 1: Start Camera
    logger.info("[TEST 1] Invoking start_camera endpoint...")
    res_start = await start_camera()
    logger.info(f"start_camera response: {res_start}")
    assert res_start.get("camera_active") is True, "Expected camera_active=True"
    logger.info("-> [PASS] Camera started successfully!")

    # Test 2: Verify MJPEG Stream Frame Generation
    logger.info("[TEST 2] Verifying MJPEG stream generator yields frames...")
    gen = generate_mjpeg_frames()
    first_frame = next(gen)
    assert len(first_frame) > 100, f"Expected non-empty JPEG frame bytes, got {len(first_frame)}"
    assert b"--frame" in first_frame, "Expected MJPEG boundary header"
    logger.info(f"-> [PASS] MJPEG stream generator successfully produced {len(first_frame)} bytes frame!")

    # Test 3: Stop Camera
    logger.info("[TEST 3] Invoking stop_camera endpoint...")
    res_stop = await stop_camera()
    logger.info(f"stop_camera response: {res_stop}")
    assert res_stop.get("camera_active") is False, "Expected camera_active=False"
    logger.info("-> [PASS] Camera stopped successfully!")

    # Test 4: Repeated START Camera
    logger.info("[TEST 4] Re-invoking start_camera endpoint (Repeated Start)...")
    res_start_again = await start_camera()
    logger.info(f"start_camera again response: {res_start_again}")
    assert res_start_again.get("camera_active") is True, "Expected camera_active=True on restart"
    logger.info("-> [PASS] Camera restarted successfully on repeated start!")

    # Clean up stop
    await stop_camera()
    logger.info("=========================================")
    logger.info("ALL PHASE 6.5 CAMERA CONTROL TESTS PASSED!")
    logger.info("=========================================")

if __name__ == "__main__":
    asyncio.run(run_camera_test_sequence())

"""Live streaming endpoints."""
from ..constants import PATH_LIVE_GOOD_TIME
from ..models import Response


class LiveMixin:
    """Live streaming endpoints."""

    def live_good_time(self) -> Response:
        """Check if it's a good time for live streaming."""
        data = self._signed_body({"_uuid": self.device.device_id})
        resp = self._post(PATH_LIVE_GOOD_TIME, data=data)
        return self._json(resp)

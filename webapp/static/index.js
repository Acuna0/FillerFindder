function deleteShow(showId) {
    fetch("/delete-show", {
      method: 'POST',
      body: JSON.stringify({ showId: showId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }
